#include "httplib.h"
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


using httplib::Request;
using httplib::Response;
using json = nlohmann::json;
namespace po = boost::program_options;

#define PORT_MIN 10000
#define PORT_MAX 20000

/**
 * Ugly globals
 */
httplib::Server server;
std::thread simulation_thread;
SimulationThreadState *simulation_thread_state;
bool simulation_log;
bool daemon_log;
int port_number;
int sleep_us;


#include <sys/socket.h>
#include <netinet/in.h>

bool isPortTaken(int port) {
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    struct sockaddr_in address;
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons( port );
    int ret_value = ::bind(sockfd, (struct sockaddr *)&address, sizeof(address));

    if (ret_value == 0) {
        close(sockfd);
        return false;
    } else if (errno == EADDRINUSE) {
        return true;
    } else {
        throw std::runtime_error("isPortTaken(): port should be either taken or not taken");
    }
}

/***********************
 ** ALL PATH HANDLERS **
 ***********************/

void displayRequest(const Request &req) {
    unsigned long max_line_length = 120;
    if (daemon_log) {
        std::cerr << req.path << " " << req.body.substr(0, max_line_length)
                  << (req.body.length() > max_line_length ? "..." : "") << std::endl;
    }
}

void setJSONResponse(Response& res, json& answer) {
    res.set_header("access-control-allow-origin", "*");
    res.set_content(answer.dump(), "application/json");
}

bool simulationHasStarted(Response &res) {
    if (simulation_thread_state != nullptr) {
        return true;
    }

    json answer;
    answer["success"] = false;
    answer["failure_cause"] = "Simulation has not been started or has been terminated";
    setJSONResponse(res, answer);
    return false;
}

void alive(const Request& req, Response& res) {
    displayRequest(req);
    if (not simulationHasStarted(res))
        return;

    // Create json answer
    json answer;
    answer["success"] = true;
    answer["alive"] = true;

    setJSONResponse(res, answer);
}



void getTime(const Request& req, Response& res) {
    displayRequest(req);
    if (not simulationHasStarted(res))
        return;

    // Retrieve simulated time from simulation thread
    auto time = simulation_thread_state->getSimulationTime();

    // Create json answer
    json answer;
    answer["success"] = true;
    answer["time"] = time;

    setJSONResponse(res, answer);
}

void getAllHostnames(const Request& req, Response& res) {
    displayRequest(req);
    if (not simulationHasStarted(res))
        return;

    // Retrieve all hostnames from simulation thread
    std::vector<std::string> hostnames = simulation_thread_state->getAllHostnames();

    // Create json answer
    json answer;
    answer["success"] = true;
    answer["hostnames"] = hostnames;

    setJSONResponse(res, answer);
}

void terminateSimulation(const Request& req, Response& res) {
    displayRequest(req);
    if (not simulationHasStarted(res))
        return;

    // Stop the simulation thread and wait for it to have stopped
    simulation_thread_state->stopSimulation();
    simulation_thread.join();

    // Create an json answer
    json answer;
    answer["success"] = true;

    setJSONResponse(res, answer);

    server.stop();
    if (daemon_log) {
        std::cerr << " PID " << getpid() << " terminated.\n";
    }
    exit(1);
}


void addTime(const Request& req, Response& res) {
    displayRequest(req);
    if (not simulationHasStarted(res))
        return;

    // Get the time to sleep from the request
    auto time_to_sleep = json::parse(req.body)["increment"].get<double>();

    // Tell the simulation thread to advance simulation time
    simulation_thread_state->advanceSimulationTime(time_to_sleep);

    json answer;
    answer["success"] = true;
    setJSONResponse(res, answer);
}


void getSimulationEvents(const Request& req, Response& res) {
    displayRequest(req);
    if (not simulationHasStarted(res))
        return;

    // Get events from the simulation thread
    std::vector<json> events;
    simulation_thread_state->getSimulationEvents(events);

    // Create json answer
    json answer;
    answer["success"] = true;
    answer["events"] = events;

    setJSONResponse(res, answer);
}

void waitForNextSimulationEvent(const Request &req, Response & res) {
    displayRequest(req);
    if (not simulationHasStarted(res))
        return;

    // Ask the simulation thread to wait until the next simulation event
    auto event = simulation_thread_state->waitForNextSimulationEvent();

    // Create json answer
    json answer;
    answer["success"] = true;
    answer["event"] = event;

    setJSONResponse(res, answer);
}

void addService(const Request& req, Response& res) {
    displayRequest(req);
    if (not simulationHasStarted(res))
        return;

    // Parse the request's body to json
    auto req_body = json::parse(req.body);

    // ask the simulation thread to add the service, and construct the json answer
    json answer;
    try {
        std::string service_name = simulation_thread_state->addService(req_body);
        answer["success"] = true;
        answer["compute_service_name"] = service_name;
    } catch (std::exception &e) {
        answer["success"] = false;
        answer["failure_cause"] = e.what();
    }

    setJSONResponse(res, answer);
}


void submitStandardJob(const Request& req, Response& res) {
    displayRequest(req);
    if (not simulationHasStarted(res))
        return;

    // Parse the request's body to json
    auto req_body = json::parse(req.body);

    // Ask the simulation thread to submit the job, and construct json answer
    json answer;
    try {
        simulation_thread_state->submitStandardJob(req_body);
        answer["success"] = true;
    } catch (std::exception &e) {
        answer["success"] = false;
        answer["failure_cause"] = e.what();
    }

    setJSONResponse(res, answer);
}


void createStandardJob(const Request& req, Response& res) {
    displayRequest(req);
    if (not simulationHasStarted(res))
        return;

    // parse the request's answer to json
    auto req_body = json::parse(req.body);


    // Ask simulation thread to create standard job and construct json answer
    json answer;
    try {
        std::string jobID = simulation_thread_state->createStandardJob(req_body);
        answer["success"] = true;
        answer["job_id"] = jobID;
    } catch (std::exception &e) {
        answer["success"] = false;
        answer["failure_cause"] = e.what();
    }

    setJSONResponse(res, answer);
}


void startSimulation(const Request& req, Response& res) {
    displayRequest(req);
    json body = json::parse(req.body);


    // Find an available port number
    int port_number;
    while (isPortTaken(port_number = PORT_MIN + rand() % (PORT_MAX - PORT_MIN)));

    // Create a shared memory segment, to which an error message will be written
    // in case of a simulation creation failure
    auto shm_segment_id = shmget(IPC_PRIVATE, 2048, IPC_CREAT | SHM_R | SHM_W);

    // Create a child process
    auto child_pid = fork();

    if (!child_pid) {

        // The child process creates a grand child, that will be adopted by
        // pid 1 (the well-known "if I create a child that creates a grand-child
        // and I kill the child, then my grand-child will never become a zombie)
        auto grand_child_pid = fork();

        if (! grand_child_pid) {

            // The grand-child creates the simulation state
            simulation_thread_state = new SimulationThreadState();
            // Start the simulation in a separate thread
            simulation_thread = std::thread(&SimulationThreadState::createAndLaunchSimulation,
                                            simulation_thread_state,
                                            simulation_log, body["platform_xml"], body["controller_hostname"], sleep_us);

            // Wait a little bit and check whether the simulation was launched successfully
            // This is pretty ugly, but will do for now
            usleep(100000);

            // If there was a simulation launch error, then put the error message in the
            // shared memory segment before exiting
            if (simulation_thread_state->simulation_launch_error) {
                simulation_thread.join(); // THIS IS NECESSARY, otherwise the exit silently segfaults!
                char *shm_segment = (char *)shmat(shm_segment_id, nullptr, 0);
                const char *to_copy = simulation_thread_state->simulation_launch_error_message.c_str();
                strcpy(shm_segment, to_copy);
                shmdt(shm_segment);
                exit(1);
            }

            // At this point, we know the simulation has been launched

            // Set up GET request handlers
            server.Get("/api/alive", alive);
            server.Get("/api/getTime", getTime);
            server.Get("/api/getAllHostnames", getAllHostnames);
            server.Get("/api/getSimulationEvents", getSimulationEvents);
            server.Get("/api/waitForNextSimulationEvent", waitForNextSimulationEvent);

            // Set up POST request handlers
            server.Post("/api/addTime", addTime);
            server.Post("/api/addService", addService);
            server.Post("/api/createStandardJob", createStandardJob);
            server.Post("/api/submitStandardJob", submitStandardJob);
            server.Post("/api/terminateSimulation", terminateSimulation);

            server.stop(); // stop the server that was listening on the main WRENCH daemon port
            if (daemon_log) {
                std::cerr << " PID " << getpid() << " listening on port " << port_number << "\n";
            }
            server.listen("0.0.0.0", port_number);
            exit(0);
        } else {
            // Very ugly sleep, but we have to check if the grand child has exited prematurely
            // (which means it's an error), or whether it is happily running
            usleep(200000);
            int stat_loc = 0;
            waitpid(grand_child_pid, &stat_loc, WNOHANG);
            exit(WEXITSTATUS(stat_loc)); // propagate grand-child's exit code (0 or 1) up
        }
    }

    // Get the child's exit code
    int stat_loc;
    waitpid(child_pid, &stat_loc, 0);

    // Create json answer that will inform the client of success or failure
    json answer;
    if (WEXITSTATUS(stat_loc) == 0) {
        answer["success"] = true;
        answer["port_number"] = port_number;
    } else {
        answer["success"] = false;
        // Grab the error message from the shared memory segment
        char *shm_segment_top = (char *)shmat(shm_segment_id, nullptr, 0);
        answer["failure_cause"] = std::string(shm_segment_top);
        shmdt(shm_segment_top);
    }

    // Destroy the shared memory segment
    shmctl(shm_segment_id, IPC_RMID, NULL);

    // Prepare the response to the client
    setJSONResponse(res, answer);
}

void error_handling(const Request& req, Response& res) {
    std::cerr << "[" << res.status << "]: " << req.path << " " << req.body << "\n";
}

/******************
 ** MAIN FUNCTION *
 ******************/

int main(int argc, char **argv) {

    // Generic lambda to check if a numeric argument is in some range
    auto in = [](const auto &min, const auto &max, char const * const opt_name) {
        return [opt_name, min, max](const auto &v){
            if (v < min || v > max) {
                throw po::validation_error
                        (po::validation_error::invalid_option_value,
                         opt_name, std::to_string(v));
            }
        };
    };

    // Parse command-line arguments
    po::options_description desc("Allowed options");
    desc.add_options()
            ("help", "Show this help message")
            ("enable-simulation-logging", po::bool_switch()->default_value(false),
             "Show full simulation log during execution")
            ("enable-daemon-logging", po::bool_switch()->default_value(false),
             "Show full daemon log during execution")
            ("port", po::value<int>()->default_value(8101)->notifier(
                    in(1024, 49151, "port")),
             "port number, between 1024 and 4951, on which this daemon will listen")
            ("sleep-us", po::value<int>()->default_value(200)->notifier(
                    in(0, 1000000, "sleep-us")),
             "number of micro-seconds, between 0 and 1000000, that the simulation thread sleeps at each iteration of its main loop (smaller means faster simulation, larger means less CPU load)")
            ;

    po::variables_map vm;
    try {
        po::store(po::parse_command_line(argc, argv, desc), vm);
        // Print help message and exit if needed
        if (vm.count("help")) {
            cout << desc << "\n";
            exit(0);
        }
        // Throw whatever exception in case argument values are erroneous
        po::notify(vm);
    } catch (std::exception &e) {
        cerr << "Error: " << e.what() << "\n";
        exit(1);
    }

    // Set some globals based on command-line arguments
    simulation_log = vm["enable-simulation-logging"].as<bool>();
    daemon_log = vm["enable-daemon-logging"].as<bool>();
    port_number = vm["port"].as<int>();
    sleep_us = vm["sleep-us"].as<int>();


    // Only set up POST request handler for "/api/startSimulation" since
    // all other API paths will be handled by a child process instead
    server.Post("/api/startSimulation", startSimulation);

    // Set some generic error handler
    server.set_error_handler(error_handling);

    // Start the web server
    if (daemon_log) {
        std::cerr << "WRENCH daemon listening on port" << port_number << "...\n";
    }
    while (true) {
        // This is in a while loop because, on Linux, the main process seems to return
        // from the listen() call below, not sure why...
        server.listen("0.0.0.0", port_number);
    }
}