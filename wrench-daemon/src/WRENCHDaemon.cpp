#include "SimulationThreadState.h"

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
    struct sockaddr_in address;
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons( port );
    int ret_value = ::bind(sock, (struct sockaddr *)&address, sizeof(address));

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
    // the child process (the simuation daemon) in case it fails on startup
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

    if (!child_pid) {

        // Stop the server that was listening on the main WRENCH daemon port
        server.stop();

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

        if (!grand_child_pid) {

            // Create the simulation state
            auto simulation_thread_state = new SimulationThreadState();

            // Start the simulation in a separate thread
            auto simulation_thread = std::thread(&SimulationThreadState::createAndLaunchSimulation,
                                            simulation_thread_state,
                                            simulation_logging, body["platform_xml"], body["controller_hostname"], sleep_us);

            // Wait a little bit and check whether the simulation was launched successfully
            // This is pretty ugly, but will do for now. It's a bit hard to do it in a different
            // wait, especially because the call to launch() could fail (or perhaps not?) in createAndLaunchSimulation()
            usleep(100000);

            // If there was a simulation launch error, then put the error message in the
            // shared memory segment before exiting
            if (simulation_thread_state->simulation_launch_error) {
                simulation_thread.join(); // THIS IS NECESSARY, otherwise the exit silently segfaults!
                // Put the error message in shared memory
                char *shm_segment = (char *)shmat(shm_segment_id, nullptr, 0);
                const char *to_copy = simulation_thread_state->simulation_launch_error_message.c_str();
                strcpy(shm_segment, to_copy);
                if (shmdt(shm_segment) == -1) {
                    perror("shmdt()");
                    exit(1);
                }
                // Terminate with a non-zero error code
                exit(1);
            }

            // Create the simulation daemon and call its run() method, which will launch the
            // HTTP server for this new simulation
            auto simulation_daemon = new SimulationDaemon(
                    daemon_logging, simulation_port_number,
                    simulation_thread_state, simulation_thread);
            simulation_daemon->run(); // never returns
            exit(0);

        } else {
            // Very ugly sleep, but we have to check if the grand child has exited prematurely
            // (which means it's an error), or whether it is happily running.
            usleep(200000);
            // Check the status of the grand-child, but non-blockingly, so that
            // if it is indeed happily running we dont get stuck here!
            int stat_loc = 0;
            if (waitpid(grand_child_pid, &stat_loc, WNOHANG) == -1) {
                perror("waitpid()");
                exit(1);
            }
            // propagate grand-child's exit code (whether 0 or non-zero) up to the parent
            exit(WEXITSTATUS(stat_loc));
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
