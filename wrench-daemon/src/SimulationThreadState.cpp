#include "httplib.h"
#include "SimulationThreadState.h"
#include "SimulationController.h"

#include <unistd.h>

#include <cstdio>
#include <string>
#include <vector>

#include <nlohmann/json.hpp>
#include <wrench.h>

void SimulationThreadState::createAndLaunchSimulation(
        bool full_log,
        std::string platform_file,
        std::string controller_host) {

    int argc = (full_log ? 2 : 1);
    char **argv = (char **)calloc(argc, sizeof(char *));
    argv[0] = strdup("wrench-daemon-simulation");
    if (argc > 1) {
        argv[1] = strdup("--wrench-full-log");
    }

    // Let WRENCH grab its own command-line arguments, if any
    simulation.init(&argc, argv);

    // Instantiate Simulated Platform
    simulation.instantiatePlatform(platform_file);

    // Check that the controller host exists
    if (not wrench::Simulation::doesHostExist(controller_host)) {
        throw std::runtime_error("There should be a host called " + controller_host + " in the XML platform file");
    }

    this->simulation_controller = simulation.add(
            new wrench::SimulationController(controller_host));

    // Add a bogus workflow to simulation_controller
    wrench::Workflow workflow;
    this->simulation_controller->addWorkflow(&workflow);

    // Start the simulation. Currently cannot start the simulation in a different thread or else it will
    // seg fault. Most likely related to how simgrid handles threads so the web wrench-daemon has to started
    // on a different thread.
    simulation.launch();
}

void SimulationThreadState::advanceSimulationTime(double seconds) {
    this->simulation_controller->advanceSimulationTime(seconds);
}

void SimulationThreadState::getEventStatuses(queue<std::string> &statuses, const time_t &time) const {
    this->simulation_controller->getEventStatuses(statuses, time);
}

//std::string SimulationThreadState::addJob(const double& requested_duration,
//                                          const unsigned int& num_nodes, const double& actual_duration) const {
//    return this->simulation_controller->addJob(requested_duration, num_nodes, actual_duration);
//}

std::string SimulationThreadState::addService(json service_spec) const {
    return this->simulation_controller->addNewService(service_spec);
}

std::vector<std::string> SimulationThreadState::getAllHostnames() const {
    return this->simulation_controller->getAllHostnames();
}


void SimulationThreadState::stopSimulation() const {
    this->simulation_controller->stopServer();
}

std::vector<std::string> SimulationThreadState::getQueue() const {
    return this->simulation_controller->getQueue();
}

double SimulationThreadState::getSimulationTime() const {
    return this->simulation_controller->getSimulationTime();
}
