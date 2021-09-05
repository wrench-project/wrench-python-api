#include "httplib.h"
#include "SimulationThreadState.h"

#include <cstdio>
#include <string>
#include <vector>
#include <thread>

#include <boost/program_options.hpp>

#include <nlohmann/json.hpp>

using httplib::Request;
using httplib::Response;
using json = nlohmann::json;

namespace po = boost::program_options;

/**
 * Ugly globals
 */
httplib::Server server;
std::thread simulation_thread;
SimulationThreadState *simulation_thread_state;
bool full_log;
int port_number;
int sleep_us;

/***********************
 ** ALL PATH HANDLERS **
 ***********************/

void displayRequest(const Request &req) {
    int max_line_length = 120;
    std::cerr << req.path << " " << req.body.substr(0, max_line_length) << (req.body.length() > max_line_length ? "..." : "") << std::endl;
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
    answer["failure_cause"] = "Simulation has not been started";
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


void startSimulation(const Request& req, Response& res) {
    displayRequest(req);
    json body = json::parse(req.body);

    // Create json answer
    json answer;

    if (simulation_thread_state != nullptr) {
        answer["success"] = false;
        answer["failure_cause"] = "Simulation is already started...";
    } else {
        // Start the simulation in a separate thread
        simulation_thread_state = new SimulationThreadState();
        try {
            simulation_thread = std::thread(&SimulationThreadState::createAndLaunchSimulation, simulation_thread_state,
                                            full_log, body["platform_xml"], body["controller_hostname"], sleep_us);
            answer["success"] = true;
        } catch (std::exception &e) {
            answer["success"] = false;
            answer["failure_cause"] = std::string(e.what());
        }
    }

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

    // exit in 1 second
    server.stop();
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

/**
 * @brief Path handling adding a service to the simulation.
 *
 * @param req HTTP request object
 * @param res HTTP response object
 */
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
            ("wrench-full-log", po::bool_switch()->default_value(false),
             "Show full simulation log during execution")
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

    full_log = vm["wrench-full-log"].as<bool>();
    port_number = vm["port"].as<int>();
    sleep_us = vm["sleep-us"].as<int>();

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
    server.Post("/api/startSimulation", startSimulation);
    server.Post("/api/terminateSimulation", terminateSimulation);

    // Set some generic error handler
    server.set_error_handler(error_handling);

    while (true) {
        auto pid = fork();
        if (!pid) { // child
            // Start the HTTP server
            simulation_thread_state = nullptr;
            std::printf("Listening on port: %d\n", port_number);
            server.listen("0.0.0.0", port_number);
        } else { // parent
            int stat_loc;
            waitpid(pid, &stat_loc, 0);
        }
    }
}