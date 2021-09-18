
#include <cstdio>
#include <string>
#include <vector>
#include <thread>
#include <boost/program_options.hpp>
#include <nlohmann/json.hpp>

#include "SimulationController.h"
#include "SimulationDaemon.h"

using json = nlohmann::json;

/**
 * @brief The Simulation Daemon's "main" method
 */
void SimulationDaemon::run() {

    // Set up GET request handlers
    server.Get("/api/alive", [this](const Request &req, Response &res) { alive(req, res); });
    server.Get("/api/getTime", [this](const Request &req, Response &res) { getTime(req, res); });
    server.Get("/api/getAllHostnames", [this](const Request &req, Response &res) { getAllHostnames(req, res); });
    server.Post("/api/standardJobGetNumTasks", [this](const Request &req, Response &res) { standardJobGetNumTasks(req, res); });
    server.Get("/api/getSimulationEvents",
               [this](const Request &req, Response &res) { getSimulationEvents(req, res); });
    server.Get("/api/waitForNextSimulationEvent",
               [this](const Request &req, Response &res) { waitForNextSimulationEvent(req, res); });

    // Set up POST request handlers
    server.Post("/api/addTime", [this](const Request &req, Response &res) { addTime(req, res); });
    server.Post("/api/addService", [this](const Request &req, Response &res) { addService(req, res); });
    server.Post("/api/createStandardJob", [this](const Request &req, Response &res) { createStandardJob(req, res); });
    server.Post("/api/submitStandardJob", [this](const Request &req, Response &res) { submitStandardJob(req, res); });
    server.Post("/api/terminateSimulation",
                [this](const Request &req, Response &res) { terminateSimulation(req, res); });

    if (daemon_logging) {
        std::cerr << " PID " << getpid() << " listening on port " << simulation_port_number << "\n";
    }
    while (true) {
        // This is in a while loop because, on Linux, it seems that sometimes the
        // server returns from the listen() call below, not sure why...
        server.listen("0.0.0.0", simulation_port_number);
    }
//    exit(0);
}

/**
 * @brief Constructor
 *
 * @param daemon_logging true if daemon logging should be printed
 * @param simulation_port_number port number on which this daemon is listening
 * @param simulation_controller the simulation controller
 * @param simulation_thread the simulation thread
 */
SimulationDaemon::SimulationDaemon(
        bool daemon_logging,
        int simulation_port_number,
        std::shared_ptr<wrench::SimulationController> simulation_controller,
        std::thread &simulation_thread) :
        daemon_logging(daemon_logging),
        simulation_port_number(simulation_port_number),
        simulation_controller(simulation_controller),
        simulation_thread(simulation_thread) {
}


/**
 * @brief Helper method for logging
 * @param req HTTP request
 */
void SimulationDaemon::displayRequest(const Request &req) const {
    unsigned long max_line_length = 120;
    if (daemon_logging) {
        std::cerr << req.path << " " << req.body.substr(0, max_line_length)
                  << (req.body.length() > max_line_length ? "..." : "") << std::endl;
    }
}

/**
 * @brief Helper method to reduce code duplication
 * @param res HTTP request
 * @param answer reply
 */
void setJSONResponse(Response &res, json &answer) {
    res.set_header("access-control-allow-origin", "*");
    res.set_content(answer.dump(), "application/json");
}

void SimulationDaemon::alive(const Request &req, Response &res) {
    SimulationDaemon::displayRequest(req);

    // Create json answer
    json answer;
    answer["success"] = true;
    answer["alive"] = true;

    setJSONResponse(res, answer);
}

/***********************
 ** ALL PATH HANDLERS **
 ***********************/

void SimulationDaemon::getTime(const Request &req, Response &res) {
    SimulationDaemon::displayRequest(req);

    // Retrieve simulated time from simulation thread
    auto time = simulation_controller->getSimulationTime();

    // Create json answer
    json answer;
    answer["success"] = true;
    answer["time"] = time;

    setJSONResponse(res, answer);
}

void SimulationDaemon::getAllHostnames(const Request &req, Response &res) {
    SimulationDaemon::displayRequest(req);

    // Retrieve all hostnames from simulation thread
    std::vector<std::string> hostnames = simulation_controller->getAllHostnames();

    // Create json answer
    json answer;
    answer["success"] = true;
    answer["hostnames"] = hostnames;

    setJSONResponse(res, answer);
}

void SimulationDaemon::standardJobGetNumTasks(const Request &req, Response &res) {
    SimulationDaemon::displayRequest(req);

    std::cerr << req.body << "\n";
    std::string job_name = json::parse(req.body)["job_name"];

    json answer;
    // Retrieve number of tasks from simulation thread
    try {
        int num_tasks = simulation_controller->getStandardJobNumTasks(job_name);
        // Create json answer
        answer["success"] = true;
        answer["num_tasks"] = num_tasks;
    } catch (std::runtime_error &e) {
        answer["success"] = false;
        answer["failure_cause"] = std::string(e.what());
    }

    setJSONResponse(res, answer);
}

void SimulationDaemon::terminateSimulation(const Request &req, Response &res) {
    displayRequest(req);

    // Stop the simulation thread and wait for it to have stopped
    simulation_controller->stopSimulation();
    simulation_thread.join();

    // Create an json answer
    json answer;
    answer["success"] = true;

    setJSONResponse(res, answer);

    server.stop();
    if (daemon_logging) {
        std::cerr << " PID " << getpid() << " terminated.\n";
    }
    exit(1);
}

void SimulationDaemon::addTime(const Request &req, Response &res) {
    this->displayRequest(req);

    // Get the time to sleep from the request
    auto time_to_sleep = json::parse(req.body)["increment"].get<double>();

    // Tell the simulation thread to advance simulation time
    simulation_controller->advanceSimulationTime(time_to_sleep);

    json answer;
    answer["success"] = true;
    setJSONResponse(res, answer);
}

void SimulationDaemon::getSimulationEvents(const Request &req, Response &res) {
    displayRequest(req);

    // Get events from the simulation thread
    std::vector<json> events;
    simulation_controller->getSimulationEvents(events);

    // Create json answer
    json answer;
    answer["success"] = true;
    answer["events"] = events;

    setJSONResponse(res, answer);
}

void SimulationDaemon::waitForNextSimulationEvent(const Request &req, Response &res) {
    this->displayRequest(req);

    // Ask the simulation thread to wait until the next simulation event
    auto event = simulation_controller->waitForNextSimulationEvent();

    // Create json answer
    json answer;
    answer["success"] = true;
    answer["event"] = event;

    setJSONResponse(res, answer);
}

void SimulationDaemon::addService(const Request &req, Response &res) {
    this->displayRequest(req);

    // Parse the request's body to json
    auto req_body = json::parse(req.body);

    // ask the simulation thread to add the service, and construct the json answer
    json answer;
    try {
        std::string service_name = simulation_controller->addService(req_body);
        answer["success"] = true;
        answer["compute_service_name"] = service_name;
    } catch (std::exception &e) {
        answer["success"] = false;
        answer["failure_cause"] = e.what();
    }

    setJSONResponse(res, answer);
}

void SimulationDaemon::submitStandardJob(const Request &req, Response &res) {
    this->displayRequest(req);

    // Parse the request's body to json
    auto req_body = json::parse(req.body);

    // Ask the simulation thread to submit the job, and construct json answer
    json answer;
    try {
        simulation_controller->submitStandardJob(req_body);
        answer["success"] = true;
    } catch (std::exception &e) {
        answer["success"] = false;
        answer["failure_cause"] = e.what();
    }

    setJSONResponse(res, answer);
}

void SimulationDaemon::createStandardJob(const Request &req, Response &res) {
    this->displayRequest(req);

    // parse the request's answer to json
    auto req_body = json::parse(req.body);

    // Ask simulation thread to create standard job and construct json answer
    json answer;
    try {
        std::string jobID = simulation_controller->createStandardJob(req_body);
        answer["success"] = true;
        answer["job_id"] = jobID;
    } catch (std::exception &e) {
        answer["success"] = false;
        answer["failure_cause"] = e.what();
    }

    setJSONResponse(res, answer);
}
