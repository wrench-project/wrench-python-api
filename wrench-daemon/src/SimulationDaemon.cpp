
#include <string>
#include <utility>
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

    // Set up GET request handler for the (likely useless) "alive" path
    server.Get("/api/alive", [this](const Request &req, Response &res) { alive(req, res); });

    // Set up POST request handler for terminating simulation
    server.Post("/api/terminateSimulation",
                [this](const Request &req, Response &res) { terminateSimulation(req, res); });

    // Set up ALL POST request handlers for API calls

    std::vector<std::string> api_paths = {
            "getTime",
            "getAllHostnames",
            "addService",
            "advanceTime",
            "createStandardJob",
            "submitStandardJob",
            "getSimulationEvents",
            "waitForNextSimulationEvent",
            "standardJobGetNumTasks"
    };

    for (auto const &path : api_paths) {
        server.Post(("/api/" + path).c_str(),
                    [this](const Request &req, Response &res) { handleAPIRequest(req, res); });
    }

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
        simulation_controller(std::move(std::move(std::move(simulation_controller)))),
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
    answer["wrench_api_request_success"] = true;
    answer["alive"] = true;

    setJSONResponse(res, answer);
}

/***********************
 ** ALL PATH HANDLERS **
 ***********************/

void SimulationDaemon::terminateSimulation(const Request &req, Response &res) {
    displayRequest(req);

    // Stop the simulation thread and wait for it to have stopped
    simulation_controller->stopSimulation();
    simulation_thread.join();

    // Create an json answer
    json answer;
    answer["wrench_api_request_success"] = true;

    setJSONResponse(res, answer);

    server.stop();
    if (daemon_logging) {
        std::cerr << " PID " << getpid() << " terminated.\n";
    }
    exit(1);
}


void SimulationDaemon::handleAPIRequest(const Request &req, Response &res) {
    this->displayRequest(req);

    json answer;
    try {
        answer = simulation_controller->processRequest(req.path, json::parse(req.body));
        answer["wrench_api_request_success"] = true;
    } catch (std::exception &e) {
        answer["wrench_api_request_success"] = false;
        answer["failure_cause"] = e.what();
    }
    setJSONResponse(res, answer);
}
