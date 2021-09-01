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

#define SIMULATION_RESET 100
#define SIMULATION_END 101
bool simulation_reset = false;

void signal_handler(int sig) {
    if (sig == SIGSEGV) {
        exit(SIMULATION_RESET);
    }
}



// Define a long function which is used multiple times to retrieve the time
#define get_time() (std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::system_clock::now().time_since_epoch()).count())

using httplib::Request;
using httplib::Response;
using json = nlohmann::json;

namespace po = boost::program_options;

httplib::Server server;

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
std::string pp_name;
int pp_seqwork;
int pp_parwork;
int num_cluster_nodes;
int num_cores_per_node;
std::string tracefile_scheme;


// GET PATHS

/**
 * @brief Path handling the current server simulated time.
 * 
 * @param req HTTP request object
 * @param res HTTP response object
 */
void getTime(const Request& req, Response& res)
{
    std::printf("Path: %s\n\n", req.path.c_str());

    json body;

    // Checks if time has started otherwise return an error.
    if (time_start == 0)
    {
        res.status = 400;
        return;
    }

    // Sets and returns the time.
    body["time"] = get_time() - time_start;
    res.set_header("access-control-allow-origin", "*");
    res.set_content(body.dump(), "application/json");
}

/**
 * @brief Path handling the retrieval of even statuses.
 * 
 * @param req HTTP request object
 * @param res HTTP response object
 */
void getQuery(const Request& req, Response& res)
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

/**
 * @brief Path handling the current jobs in the queue running or waiting.
 * 
 * @param req HTTP request object
 * @param res HTTP response object
 */
void getQueue(const Request& req, Response& res)
{
    std::printf("Path: %s\n\n", req.path.c_str());

    json body;
    body["time"] = get_time() - time_start;
    body["queue"] = simulation_thread_state->getQueue();;

    res.set_header("access-control-allow-origin", "*");
    res.set_content(body.dump(), "application/json");
}

// POST PATHS

/**
 * @brief Path handling the starting of the simulation.
 * 
 * @param req HTTP request object
 * @param res HTTP response object
 */
void start(const Request& req, Response& res)
{
    std::printf("Path: %s\nBody: %s\n\n", req.path.c_str(), req.body.c_str());

    time_start = get_time();
    res.set_header("access-control-allow-origin", "*");


    // Stop simulation
    simulation_thread_state->stopSimulation();
    
    // Join with simulation thread
    simulation_thread.join();

    simulation_reset = true;

    json body;
    body["pp_name"] = pp_name;
    body["pp_seqwork"] = pp_seqwork;
    body["pp_parwork"] = pp_parwork;
    body["num_cluster_nodes"] = num_cluster_nodes;
    res.set_header("access-control-allow-origin", "*");
    res.set_content(body.dump(), "application/json");

    server.stop(); // will restart! like in a reset, in case this is a page reload
}

/**
 * @brief Path handling the stopping of the simulation.
 * 
 * @param req HTTP request object
 * @param res HTTP response object
 */
void stop(const Request& req, Response& res)
{
    std::printf("Path: %s\nBody: %s\n\n", req.path.c_str(), req.body.c_str());

    // Stop the server
    simulation_thread_state->stopSimulation();

    // Join with the thread
    simulation_thread.join();
    // Erase the simulated state
    res.set_header("access-control-allow-origin", "*");
    std::exit(0);
}

/**
 * @brief Path handling the resetting of the simulation.
 *
 * @param req HTTP request object
 * @param res HTTP response object
 */
void reset(const Request& req, Response& res)
{
    std::printf("Path: %s\nBody: %s\n\n", req.path.c_str(), req.body.c_str());

    // Stop simulation
    simulation_thread_state->stopSimulation();
    // Join with simulation thread
    simulation_thread.join();

    simulation_reset = true;

    res.set_header("access-control-allow-origin", "*");
    server.stop();
}

/**
 * @brief Path handling adding of 1 minute to current server simulated time.
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
 * @brief Path handling adding a job to the simulated batch scheduler.
 * 
 * @param req HTTP request object
 * @param res HTTP response object
 */
void addJob(const Request& req, Response& res)
{
    json req_body = json::parse(req.body);
    std::printf("Path: %s\nBody: %s\n\n", req.path.c_str(), req.body.c_str());

    // Retrieve task creation info from request body
    auto requested_duration = req_body["job"]["durationInSec"].get<double>();
    auto num_nodes = req_body["job"]["numNodes"].get<int>();
    double actual_duration = (double)pp_seqwork + ((double)pp_parwork / num_nodes);
    json body;

    // Pass parameters in to function to add a job.
    std::string jobID = simulation_thread_state->addJob(requested_duration, num_nodes, actual_duration);

    // Retrieve the return value from adding ajob to determine if successful.
    if(!jobID.empty())
    {
        body["time"] = get_time() - time_start;
        body["jobID"] = jobID;
        body["success"] = true;
    }
    else
    {
        body["time"] = get_time() - time_start;
        body["success"] = false;
    }

    res.set_header("access-control-allow-origin", "*");
    res.set_content(body.dump(), "application/json");
}

/**
 * @brief Path handling canceling a job from the simulated batch scheduler.
 * 
 * @param req HTTP request object
 * @param res HTTP response object
 */
void cancelJob(const Request& req, Response& res)
{
    json req_body = json::parse(req.body);
    std::printf("Path: %s\nBody: %s\n\n", req.path.c_str(), req.body.c_str());
    json body;
    body["time"] = get_time() - time_start;
    body["success"] = false;
    // Send cancel job to wms and set success in job cancelation if can be done.
    if(simulation_thread_state->cancelJob(req_body["jobName"].get<std::string>()))
        body["success"] = true;

    res.set_header("access-control-allow-origin", "*");
    res.set_content(body.dump(), "application/json");
}

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
int real_main(int argc, char **argv)
{
    int port_number;

    // Save the arguments
    original_argc = argc;
    original_argv = (char **) calloc(argc, sizeof(char *));
    for (int i = 0; i < argc; i++) {
        original_argv[i] = (char *)calloc(strlen(argv[i]) + 1, sizeof(char));
        strcpy(original_argv[i], argv[i]);
    }

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
            ("help", "show help message")
            ("wrench-full-log", "wrench-specific flag")
            ("nodes", po::value<int>()->default_value(4)->notifier(
                    in(1, INT_MAX, "nodes")), "number of compute nodes in the cluster")
            ("cores", po::value<int>()->default_value(1)->notifier(
                    in(1, INT_MAX, "cores")), "number of cores per compute node")
            ("tracefile", po::value<std::string>()->default_value("none"), "background workload trace file scheme (none, rightnow, backfilling, choices)")
            ("pp_name", po::value<std::string>()->default_value("parallel_program"), "parallel program name")
            ("pp_seqwork", po::value<int>()->default_value(600)->notifier(
                    in(1, INT_MAX, "pp_seqwork")), "parallel program's sequential work in seconds")
            ("pp_parwork", po::value<int>()->default_value(3600)->notifier(
                    in(1, INT_MAX, "pp_parwork")), "parallel program's parallelizable work in seconds")
            ("port", po::value<int>()->default_value(80)->notifier(
                    in(1, INT_MAX, "port")), "server port (if 80, may need to sudo)")
            ;

    po::variables_map vm;
    try {
        po::store(po::parse_command_line(argc, argv, desc), vm);
        po::notify(vm);
    } catch (std::exception &e) {
        cerr << "Error: " << e.what() << "\n";
        return 1;
    }
    num_cluster_nodes = vm["nodes"].as<int>();
    num_cores_per_node = vm["cores"].as<int>();
    tracefile_scheme = vm["tracefile"].as<std::string>();
    pp_name = vm["pp_name"].as<std::string>();
    pp_seqwork = vm["pp_seqwork"].as<int>();
    pp_parwork = vm["pp_parwork"].as<int>();
    port_number = vm["port"].as<int>();

    // Print help message and exit if needed
    if (vm.count("help")) {
        cout << desc << "\n";
        return 1;
    }

    // Print some logging
    cerr << "Simulating a cluster with " << num_cluster_nodes << " " << num_cores_per_node << "-core nodes.\n";
    cerr << "Background workload using scheme " + tracefile_scheme << ".\n";
    cerr << "Parallel program is called " << pp_name << ".\n";
    cerr << "Its sequential work is " << pp_seqwork << " seconds.\n";
    cerr << "Its parallel work is " << pp_parwork << " seconds.\n";

    // Handle GET requests
    server.Get("/api/time", getTime);
    server.Get("/api/query", getQuery);

    // Handle POST requests
    server.Post("/api/start", start);
    server.Post("/api/stop", stop);
    server.Post("/api/reset", reset);
    server.Post("/api/addTime", addTime);
    server.Post("/api/addJob", addJob);
    server.Post("/api/cancelJob", cancelJob);
    server.Post("/api/getQueue", getQueue);

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
    simulation_thread = std::thread(&SimulationThreadState::createAndLaunchSimulation,
                                    simulation_thread_state, original_argc, original_argv,
                                    num_cluster_nodes, num_cores_per_node, tracefile_scheme);

    // Start the server
    std::printf("Listening on port: %d\n", port_number);
    server.listen("0.0.0.0", port_number);

    return (simulation_reset ? SIMULATION_RESET : SIMULATION_END);
}

/**
 * @brief Main function
 * @param argc
 * @param argv
 * @return
 */

int main(int argc, char **argv) {

    // Loop that keeps restarting the server every time it stops
    // due to a simulation reset
    while (true) {
        pid_t child = fork();
        if (!child) {
            // Set the start time
            time_start = get_time();
            // Setup a handled for segfault, while waiting to figure out
            // why rapid-fire simulation resets cause segfaults on Mac even
            // though valgrind shows no problems in linux
            signal(SIGSEGV, signal_handler);
            // Call the real main function which returns:
            //  - SIMULATION_END if simulation should stop
            //  - SIMULATION_RESET if simulation should reset and restart
            int ret_value = real_main(argc, argv);
            exit(ret_value);
        }

        int exit_code = 0;
        waitpid(child, &exit_code, 0);
        exit_code = WEXITSTATUS(exit_code);

        if (exit_code == SIMULATION_RESET) {
            std::cerr << "Simulation reset!\n";
            continue;
        } else {
            break;
        }
    }
    exit(0);
}
