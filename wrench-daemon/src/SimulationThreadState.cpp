#include "httplib.h"
#include "SimulationThreadState.h"
#include "SimulationController.h"

#include <string>
#include <utility>
#include <vector>

#include <wrench.h>

/**
 * @brief Method to create and launch the simulation, which is called in a thread inside a child process.
 *        To be able to notify the parent process of the nature of an error, if any, this method
 *        simple sets an error message variable and returns
 *
 * @param full_log: whether to show all simulation log
 * @param platform_xml: XML platform description (an XML string - not a file path)
 * @param controller_host: hostname of the host that will run the controller
 * @param sleep_us: number of microseconds to sleep at each iteration of the main loop
 */
void SimulationThreadState::createAndLaunchSimulation(
        bool full_log,
        const std::string& platform_xml,
        const std::string& controller_host,
        int sleep_us) {

    this->simulation_launch_error = false;

    try {

        int argc = (full_log ? 2 : 1);
        char **argv = (char **) calloc(argc, sizeof(char *));
        argv[0] = strdup("wrench-daemon-simulation");
        if (argc > 1) {
            argv[1] = strdup("--wrench-full-log");
        }

        // Let WRENCH grab its own command-line arguments, if any
        simulation.init(&argc, argv);

        // Create tmp XML platform file
        std::string platform_file_path = "/tmp/wrench_daemon_platform_file_" + std::to_string(getpid()) + ".xml";
        std::ofstream platform_file(platform_file_path);
        platform_file << platform_xml;
        platform_file.close();

        // Instantiate Simulated Platform
        try {
            simulation.instantiatePlatform(platform_file_path);
            // Erase the XML platform file
            remove(platform_file_path.c_str());
        } catch (std::exception &e) {
            // Erase the XML platform file
            remove(platform_file_path.c_str());
            throw std::runtime_error(e.what());
        }

        // Check that the controller host exists
        if (not wrench::Simulation::doesHostExist(controller_host)) {
            throw std::runtime_error("The platform does not contain a controller host with name " + controller_host);
        }

        this->simulation_controller = simulation.add(
                new wrench::SimulationController(controller_host, sleep_us));

        // Add a bogus workflow to simulation_controller
        wrench::Workflow workflow;
        this->simulation_controller->addWorkflow(&workflow);

        // Start the simulation.
        simulation.launch();

    } catch (std::exception &e) {

        this->simulation_launch_error = true;
        this->simulation_launch_error_message = std::string(e.what());
        return;
    }

}

void SimulationThreadState::advanceSimulationTime(double seconds) const {
    this->simulation_controller->advanceSimulationTime(seconds);
}

void SimulationThreadState::getSimulationEvents(std::vector<json> &events) const {
    this->simulation_controller->getSimulationEvents(events);
}

json SimulationThreadState::waitForNextSimulationEvent() const {
    return this->simulation_controller->waitForNextSimulationEvent();
}

std::string SimulationThreadState::addService(json service_spec) const {
    return this->simulation_controller->addNewService(std::move(service_spec));
}

std::vector<std::string> SimulationThreadState::getAllHostnames() const {
    return this->simulation_controller->getAllHostnames();
}

void SimulationThreadState::stopSimulation() const {
    this->simulation_controller->stopSimulation();
}


double SimulationThreadState::getSimulationTime() const {
    return this->simulation_controller->getSimulationTime();
}

std::string SimulationThreadState::createStandardJob(json task_spec) const {
    return this->simulation_controller->createStandardJob(std::move(task_spec));
}

void SimulationThreadState::submitStandardJob(json submission_spec) const {
    this->simulation_controller->submitStandardJob(std::move(submission_spec));
}
