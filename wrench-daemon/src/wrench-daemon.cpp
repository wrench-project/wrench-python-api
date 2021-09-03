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

/***********************
 ** ALL PATH HANDLERS **
 ***********************/

void getTime(const Request& req, Response& res) {
    std::cerr << req.path << " " << req.body << std::endl;

    // Retrieve simulated time from simulation thread
    auto time = simulation_thread_state->getSimulationTime();

    // Create json answer
    json answer;
    answer["time"] = time;

    // Send answer back
    res.set_header("access-control-allow-origin", "*");
    res.set_content(answer.dump(), "application/json");
}

void getAllHostnames(const Request& req, Response& res) {
    std::cerr << req.path << " " << req.body << std::endl;

    // Retrieve all hostnames from simulation thread
    std::vector<std::string> hostnames = simulation_thread_state->getAllHostnames();

    // Create json answer
    json answer;
    answer["hostnames"] = hostnames;

    // Send answer back
    res.set_header("Access-Control-Allow-Origin", "*");
    res.set_content(answer.dump(), "application/json");
}

void stop(const Request& req, Response& res) {
    std::cerr << req.path << " " << req.body << std::endl;

    // Stop the simulation thread and wait for it to have stopped
    simulation_thread_state->stopSimulation();
    simulation_thread.join();

    // Erase the simulated state
    res.set_header("access-control-allow-origin", "*");

    // Terminate
    std::exit(0);
}


void addTime(const Request& req, Response& res) {
    std::cerr << req.path << " " << req.body << std::endl;

    // Get the time to sleep from the request
    auto time_to_sleep = json::parse(req.body)["increment"].get<double>();

    // Tell the simulation thread to advance simulation time
    simulation_thread_state->advanceSimulationTime(time_to_sleep);
}


void getSimulationEvents(const Request& req, Response& res) {
    std::cerr << req.path << " " << req.body << std::endl;

    // Get events from the simulation thread
    std::vector<json> events;
    simulation_thread_state->getSimulationEvents(events);

    // Create json answer
    json answer;
    answer["events"] = events;

    // Send answer back
    res.set_header("access-control-allow-origin", "*");
    res.set_content(answer.dump(), "application/json");
}

void waitForNextSimulationEvent(const Request &req, Response & res) {
    std::cerr << req.path << " " << req.body << std::endl;

    // Ask the simulation thread to wait until the next simulation event
    auto event = simulation_thread_state->waitForNextSimulationEvent();

    // Create json answer
    json answer;
    answer["event"] = event;

    // Send answer back
    res.set_header("access-control-allow-origin", "*");
    res.set_content(answer.dump(), "application/json");
}

/**
 * @brief Path handling adding a service to the simulation.
 *
 * @param req HTTP request object
 * @param res HTTP response object
 */
void addService(const Request& req, Response& res) {
    std::cerr << req.path << " " << req.body << "\n";

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

    // Send answer back
    res.set_header("access-control-allow-origin", "*");
    res.set_content(answer.dump(), "application/json");
}


void submitStandardJob(const Request& req, Response& res) {
    std::cerr << req.path << " " << req.body << "\n";

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

    // Send answer back
    res.set_header("access-control-allow-origin", "*");
    res.set_content(answer.dump(), "application/json");
}


void createStandardJob(const Request& req, Response& res) {
    std::cerr << req.path << " " << req.body << "\n";

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

    // Send answer back
    res.set_header("access-control-allow-origin", "*");
    res.set_content(answer.dump(), "application/json");
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
            ("platform", po::value<std::string>()->required(),
             "Path to the XML file that described the simulated platform")
            ("controller-host", po::value<std::string>()->required(),
             "Host in the (simulated) platform on which the controller process will be running")
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

    auto full_log = vm["wrench-full-log"].as<bool>();
    auto platform_file = vm["platform"].as<std::string>();
    auto controller_host = vm["controller-host"].as<std::string>();
    auto port_number = vm["port"].as<int>();
    auto sleep_us = vm["sleep-us"].as<int>();

    // Check that platform file is available for reading
    ifstream my_file(platform_file);
    if (not my_file.good()) {
        cerr << "Platform file \"" + platform_file + "\" not found or unreadable\n";
        return 1;
    }

    // Set up GET request handlers
    server.Get("/api/getTime", getTime);
    server.Get("/api/getAllHostnames", getAllHostnames);
    server.Get("/api/getSimulationEvents", getSimulationEvents);
    server.Get("/api/waitForNextSimulationEvent", waitForNextSimulationEvent);

    // Set up POST request handlers
    server.Post("/api/addTime", addTime);
    server.Post("/api/addService", addService);
    server.Post("/api/createStandardJob", createStandardJob);
    server.Post("/api/submitStandardJob", submitStandardJob);
    server.Post("/api/stop", stop);

    // Set some generic error handler
    server.set_error_handler(error_handling);

    // Start the simulation in a separate thread
    simulation_thread_state = new SimulationThreadState();
    simulation_thread = std::thread(&SimulationThreadState::createAndLaunchSimulation, simulation_thread_state,
                                    full_log, platform_file, controller_host, sleep_us);

    // Start the HTTP server
    std::printf("Listening on port: %d\n", port_number);
    server.listen("0.0.0.0", port_number);

    exit(0);
}