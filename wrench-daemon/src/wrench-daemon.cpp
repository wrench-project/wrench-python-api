#include "httplib.h"
#include "SimulationThreadState.h"

#include <unistd.h>

#include <chrono>
#include <cstdio>
#include <string>
#include <vector>
#include <thread>

#include <boost/program_options.hpp>

#include <nlohmann/json.hpp>
#include <wrench.h>

#include <sys/types.h>
#include <sys/wait.h>

#include <signal.h>

// Define a long function which is used multiple times to retrieve the time
#define get_time() (std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::system_clock::now().time_since_epoch()).count())

using httplib::Request;
using httplib::Response;
using json = nlohmann::json;

namespace po = boost::program_options;

httplib::Server server;

bool simulation_has_been_launched = false;

/**
 * @brief Time offset used to calculate simulation time.
 * 
 * The time in milliseconds used to subtract from the current time to get the simulated time which starts at 0.
 */
time_t time_start = 0;

std::thread simulation_thread;
SimulationThreadState *simulation_thread_state;

/**
 * Ugly globals
 */
int original_argc;
char **original_argv;

/**
 * @brief Path handling the current wrench-daemon simulated time.
 * 
 * @param req HTTP request object
 * @param res HTTP response object
 */
void getTime(const Request& req, Response& res)
{
    std::printf("Path: %s\n\n", req.path.c_str());

    json body;

    double time_to_return;

    if (!simulation_has_been_launched) {
        time_to_return = 0.0;
    } else {
        time_to_return = simulation_thread_state->getSimulationTime();
    }

    // Sets and returns the time.
    body["time"] = time_to_return;
    res.set_header("access-control-allow-origin", "*");
    res.set_content(body.dump(), "application/json");
}

/**
 * @brief Path handling the retrieval of even statuses.
 * 
 * @param req HTTP request object
 * @param res HTTP response object
 */
void getEvents(const Request& req, Response& res)
{
    // Create queue to hold event statuses
    std::queue<std::string> status;
    std::vector<std::string> events;

    // Retrieves event statuses from servers and
    simulation_thread_state->getEventStatuses(status, (get_time() - time_start) / 1000);

    while(!status.empty())
    {
        events.push_back(status.front());
        status.pop();
    }

    json body;
    auto event_list = events;
    body["time"] = get_time() - time_start;
    body["events"] = event_list;
    res.set_header("Access-Control-Allow-Origin", "*");
    res.set_content(body.dump(), "application/json");
}


// POST PATHS


/**
 * @brief Path handling the stopping of the simulation.
 * 
 * @param req HTTP request object
 * @param res HTTP response object
 */
void stop(const Request& req, Response& res)
{
    std::printf("Path: %s\nBody: %s\n\n", req.path.c_str(), req.body.c_str());

    // Stop the simulation thread and wait for it to have stopped
    simulation_thread_state->stopSimulation();
    simulation_thread.join();

    // Erase the simulated state
    res.set_header("access-control-allow-origin", "*");

    // Exit
    std::exit(0);
}

/**
 * @brief Path handling adding time to current wrench-daemon simulated time.
 *
 * @param req HTTP request object
 * @param res HTTP response object
 */
void addTime(const Request& req, Response& res)
{
    std::printf("Path: %s\nBody: %s\n\n", req.path.c_str(), req.body.c_str());
    std::queue<std::string> status;
    std::vector<std::string> events;

    json req_body = json::parse(req.body);

    time_start -= req_body["increment"].get<int>() * 1000;

    // Retrieve the event statuses during the  skip period.
    simulation_thread_state->getEventStatuses(status, (get_time() - time_start) / 1000);
    cerr << "status.size() = " << status.size()  << "\n";

    while(!status.empty())
    {
        events.push_back(status.front());
        status.pop();
    }

    // Let the simulation catch up
    while ((get_time() - time_start) / 1000 > simulation_thread_state->getSimulationTime()) {
        usleep(1000);
    }

    json body;
    auto event_list = events;
    body["time"] = get_time() - time_start;
    body["events"] = event_list;
    res.set_header("access-control-allow-origin", "*");
    res.set_content(body.dump(), "application/json");
}

/**
 * @brief Path handling adding a service to the simulation.
 *
 * @param req HTTP request object
 * @param res HTTP response object
 */
void addService(const Request& req, Response& res)
{
    std::cerr << req.path << ": " << req.body << "\n";
    json req_body;
    try {
        req_body = json::parse(req.body);
    } catch (std::exception &e) {
        throw;
    }

    std::string service_name = simulation_thread_state->addService(req_body);

    json body;
    body["service_name"] = service_name;

    res.set_header("access-control-allow-origin", "*");
    res.set_content(body.dump(), "application/json");
}


/**
 * @brief Path handling submiting a Job to some compute service.
 * 
 * @param req HTTP request object
 * @param res HTTP response object
 */
void submitStandardJob(const Request& req, Response& res)
{
    json req_body = json::parse(req.body);
    std::printf("Path: %s\nBody: %s\n\n", req.path.c_str(), req.body.c_str());

    throw std::runtime_error("submitStandardJob NOT IMPLEMENTED YET");
    // Retrieve job info from request body: TODO
//    auto requested_duration = req_body["job"]["durationInSec"].get<double>();
//    auto num_nodes = req_body["job"]["numNodes"].get<int>();
//    double actual_duration = (double)pp_seqwork + ((double)pp_parwork / num_nodes);

    json body;

    // Pass parameters in to function to add a job.
    //std::string jobID = simulation_thread_state->submitJob(TODO);

//    // Retrieve the return value from adding ajob to determine if successful.
//    if(!jobID.empty())
//    {
//        body["time"] = get_time() - time_start;
//        body["jobID"] = jobID;
//        body["success"] = true;
//    }
//    else
//    {
//        body["time"] = get_time() - time_start;
//        body["success"] = false;
//    }

    res.set_header("access-control-allow-origin", "*");
    res.set_content(body.dump(), "application/json");
}

///**
// * @brief Path handling canceling a job from the simulated batch scheduler.
// *
// * @param req HTTP request object
// * @param res HTTP response object
// */
//void cancelJob(const Request& req, Response& res)
//{
//    json req_body = json::parse(req.body);
//    std::printf("Path: %s\nBody: %s\n\n", req.path.c_str(), req.body.c_str());
//    json body;
//    body["time"] = get_time() - time_start;
//    body["success"] = false;
//    // Send cancel job to simulation_controller and set success in job cancelation if can be done.
//    if(simulation_thread_state->cancelJob(req_body["jobName"].get<std::string>()))
//        body["success"] = true;
//
//    res.set_header("access-control-allow-origin", "*");
//    res.set_content(body.dump(), "application/json");
//}

// ERROR HANDLING

/**
 * @brief Generic path handling for errors.
 * 
 * @param req HTTP request object
 * @param res HTTP response object
 */
void error_handling(const Request& req, Response& res)
{
    std::printf("%d: %s|%s\n", res.status, req.path.c_str(), req.body.c_str());
}

/**
 * @brief Real main function
 * @param argc
 * @param argv
 * @return
 */
int main(int argc, char **argv)
{
//    // Save the original command-line arguments
//    original_argc = argc;
//    original_argv = (char **) calloc(argc, sizeof(char *));
//    for (int i = 0; i < argc; i++) {
//        original_argv[i] = (char *)calloc(strlen(argv[i]) + 1, sizeof(char));
//        strcpy(original_argv[i], argv[i]);
//    }

    // Generic lambda to check if a number is in some range
    auto in = [](const auto &min, const auto &max, char const * const opt_name){
        return [opt_name, min, max](const auto &v){
            if(v < min || v > max){
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

    // Check that platform file is available for reading
    ifstream my_file(platform_file);
    if (not my_file.good()) {
        cerr << "Platform file \"" + platform_file + "\" not found or unreadable\n";
        return 1;
    }

    // Handle GET requests
    server.Get("/api/time", getTime);
    server.Get("/api/getEvents", getEvents);

    // Handle POST requests
    server.Post("/api/addTime", addTime);
    server.Post("/api/addService", addService);
    server.Post("/api/submitStandardJob", submitStandardJob);
    server.Post("/api/stop", stop);

    // Set some generic error handler
    server.set_error_handler(error_handling);

    // Path is relative so if you build in a different directory, you will have to change the relative path.
    // Currently set so that it can try find the client directory in any location. 
    // Current implementation would have a security risk
    // since any file in that directory can be loaded.
    server.set_mount_point("/", "../../client");
    server.set_mount_point("/", "../client");
    server.set_mount_point("/", ".client");

    // Start the simulation in a separate thread
    simulation_thread_state = new SimulationThreadState();
    simulation_thread = std::thread(&SimulationThreadState::createAndLaunchSimulation, simulation_thread_state,
                                    full_log, platform_file, controller_host);

    // Start the wrench-daemon
    std::printf("Listening on port: %d\n", port_number);
    server.listen("0.0.0.0", port_number);

    exit(0);
}

