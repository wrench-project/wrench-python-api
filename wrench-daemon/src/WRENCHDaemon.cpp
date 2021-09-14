#include "SimulationLauncher.h"

#include <cstdio>
#include <string>
#include <vector>
#include <thread>
#include <boost/program_options.hpp>
#include <nlohmann/json.hpp>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/shm.h>

#include <WRENCHDaemon.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <SimulationDaemon.h>

using json = nlohmann::json;

// Range of ports that simulation daemons can listen on
#define PORT_MIN 10000
#define PORT_MAX 20000


/**
 * @brief Constructor
 * @param simulation_logging true if simulation logging should be printed
 * @param daemon_logging true if daemon logging should be printed
 * @param port_number port number on which to listen
 * @param sleep_us number of micro-seconds or real time that the simulation daemon's simulation controller
 *        thread should sleep at each iteration
 */
WRENCHDaemon::WRENCHDaemon(bool simulation_logging,
                           bool daemon_logging,
                           int port_number,
                           int sleep_us) :
        simulation_logging(simulation_logging),
        daemon_logging(daemon_logging),
        port_number(port_number),
        sleep_us(sleep_us) {
}


/**
 * @brief Helper method to check whether a port is available for binding/listening
 * @param port the port number
 * @return true if the port is taken, false if it is available
 */
bool WRENCHDaemon::isPortTaken(int port) {
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    struct sockaddr_in address{};
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons( port );
    auto ret_value = ::bind(sock, (struct sockaddr *)&address, sizeof(address));

    if (ret_value == 0) {
        close(sock);
        return false;
    } else if (errno == EADDRINUSE) {
        close(sock);
        return true;
    } else {
        throw std::runtime_error("isPortTaken(): port should be either taken or not taken");
    }
}

/***********************
 ** ALL PATH HANDLERS **
 ***********************/

/**
 * @brief Method to handle /api/startSimulation path
 * @param req HTTP request
 * @param res answer
 */
void WRENCHDaemon::startSimulation(const Request& req, Response& res) {
    // Print some logging
    unsigned long max_line_length = 120;
    if (daemon_logging) {
        std::cerr << req.path << " " << req.body.substr(0, max_line_length)
                  << (req.body.length() > max_line_length ? "..." : "") << std::endl;
    }

    // Parse the HTTP request's data
    json body = json::parse(req.body);

    // Find an available port number on which the simulation daemon will be able to run
    int simulation_port_number;
    while (isPortTaken(simulation_port_number = PORT_MIN + rand() % (PORT_MAX - PORT_MIN)));

    // Create a shared memory segment, to which an error message will be written by
    // the child process (the simulation daemon) in case it fails on startup
    // in case of a simulation creation failure
    auto shm_segment_id = shmget(IPC_PRIVATE, 2048, IPC_CREAT | SHM_R | SHM_W);
    if (shm_segment_id == -1) {
        perror("shmget()");
        exit(1);
    }

    // Create a child process
    auto child_pid = fork();
    if (child_pid == -1) {
        perror("fork()");
        exit(1);
    }

    if (!child_pid) { // The child process

        // Stop the server that was listening on the main WRENCH daemon port
        server.stop();

        // Create a pipe for communication with my child (aka the grand-child)
        int fd[2];
        if (pipe(fd) == -1) {
            perror("pipe()");
            exit(1);
        }

        // The child process creates a grand child, that will be adopted by
        // pid 1 (the well-known "if I create a child that creates a grand-child
        // and I kill the child, then my grand-child will never become a zombie" trick). 
        // This trick is a life-saver here, since setting up a SIGCHLD handler
        // to reap children would get in the way of what we need to do in the code hereafter.
        auto grand_child_pid = fork();
        if (grand_child_pid == -1) {
            perror("fork()");
            exit(1);
        }

        if (!grand_child_pid) { // the grand-child

            // close read end of the pipe
            close(fd[0]);

            // Create the simulation launcher
            auto simulation_launcher = new SimulationLauncher();

            // mutex/condvar for synchronization with the simulation thread I am about to create
            std::mutex guard;
            std::condition_variable signal;

            // Launch the simulation in a separate thread
            auto simulation_thread = std::thread([simulation_launcher, this, body, &guard, &signal] () {
                // Create simulation
                simulation_launcher->createSimulation(this->simulation_logging, body["platform_xml"], body["controller_hostname"], this->sleep_us);
                // Signal the parent thread that simulation creation has been done, successfully or not
                {
                    std::unique_lock<std::mutex> lock(guard);
                    signal.notify_one();
                }
                // If no failure, then proceed with the launch!
                if (not simulation_launcher->launchError()) {
                    simulation_launcher->launchSimulation();
                }
            });

            // Waiting for the simulation thread to have created the simulation, successfully or not
            {
                std::unique_lock<std::mutex> lock(guard);
                signal.wait(lock);
            }

            // If there was a simulation launch error, then put the error message in the
            // shared memory segment before exiting
            if (simulation_launcher->launchError()) {
                simulation_thread.join(); // THIS IS NECESSARY, otherwise the exit silently segfaults!
                // Put the error message in shared memory
                char *shm_segment = (char *)shmat(shm_segment_id, nullptr, 0);
                const char *to_copy = strdup(simulation_launcher->launchErrorMessage().c_str());
                strcpy(shm_segment, to_copy);
                if (shmdt(shm_segment) == -1) {
                    perror("shmdt()"); // just as a weird warning
                }
                // Write to the parent
                bool success = false;
                if (write(fd[1], &success, sizeof(bool)) == -1) {
                    perror("write()");
                }
                // Close the write-end of the pipe
                close(fd[1]);
                // Terminate with a non-zero error code, just for kicks (nbody's calling waitpid)
                exit(1);
            }

            // Write to the pipe that everything's ok and close it
            bool success = true;
            if (write(fd[1], &success, sizeof(bool)) == -1) {
                perror("write()");
                exit(1);
            }
            // Close the write-end of the pipe
            close(fd[1]);

            // Create a simulation daemon
            auto simulation_daemon = new SimulationDaemon(
                    daemon_logging, simulation_port_number,
                    simulation_launcher->getController(), simulation_thread);

            // Start the HTTP server for this particular simulation
            simulation_daemon->run(); // never returns
            exit(0); // is never executed

        } else {

            // close write end of the pipe
            close(fd[1]);

            // Wait to hear from the pipe
            bool success;
            auto bytes_read = read(fd[0], &success, sizeof(bool));
            if (bytes_read == -1) { // child failure
                success = false;
            }

            // If success exit(0) otherwise exit(1)
            exit(not success);
        }
    }


    // Wait for the child to finish and get its exit code
    int stat_loc;
    if (waitpid(child_pid, &stat_loc, 0) == -1) {
        perror("waitpid()");
        exit(1);
    }

    // Create json answer that will inform the client of success or failure, based on
    // child's exit code (which was relayed to this process from the grand-child
    json answer;
    if (WEXITSTATUS(stat_loc) == 0) {
        answer["success"] = true;
        answer["port_number"] = simulation_port_number;
    } else {
        answer["success"] = false;
        // Grab the error message from the shared memory segment
        char *shm_segment_top = (char *)shmat(shm_segment_id, nullptr, 0);
        answer["failure_cause"] = std::string(shm_segment_top);
        if (shmdt(shm_segment_top) == -1) {
            perror("shmdt()");
            exit(1);
        }
    }

    // Destroy the shared memory segment (important, since there is a limited
    // number of them we can create, and besides we should clean-up after ourselves)
    if (shmctl(shm_segment_id, IPC_RMID, nullptr) == -1) {
        perror("shmctl()");
        exit(1);
    }

    // Prepare the response to the client
    res.set_header("access-control-allow-origin", "*");
    res.set_content(answer.dump(), "application/json");
}

/**
 * @brief A generic error handler that simply prints some information
 * @param req the HTTP request
 * @param res the HTTP response
 */
void WRENCHDaemon::error_handling(const Request& req, Response& res) {
    std::cerr << "[" << res.status << "]: " << req.path << " " << req.body << "\n";
}

/**
 * @brief The WRENCH daemon's "main" method
 */
void WRENCHDaemon::run() {

    // Only set up POST request handler for "/api/startSimulation" since
    // all other API paths will be handled by a simulation daemon instead
    server.Post("/api/startSimulation", [this] (const Request& req, Response& res) { this->startSimulation(req, res); });

    // Set some generic error handler
    server.set_error_handler([] (const Request& req, Response& res) { WRENCHDaemon::error_handling(req, res); });

    // Start the web server
    if (daemon_logging) {
        std::cerr << "WRENCH daemon listening on port " << port_number << "...\n";
    }
    while (true) {
        // This is in a while loop because, on Linux, the main process seems to return
        // from the listen() call below, not sure why... perhaps this while loop
        // could be removed, but it likely doesn't hurt
        server.listen("0.0.0.0", port_number);
    }
}