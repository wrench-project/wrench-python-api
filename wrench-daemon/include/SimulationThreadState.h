#ifndef WRENCH_CSSI_POC_SIMULATION_THREAD_STATE_H
#define WRENCH_CSSI_POC_SIMULATION_THREAD_STATE_H

#include "SimulationController.h"
#include <unistd.h>
#include <nlohmann/json.hpp>

/**
 * @brief A class that handles all simulation changes and holds all simulation state.
 */
class SimulationThreadState {

public:
    std::shared_ptr<wrench::SimulationController> simulation_controller;
    wrench::Simulation simulation;

    ~SimulationThreadState() = default;

    void getSimulationEvents(std::vector<json> &events) const;
    json waitForNextSimulationEvent() const;


    std::string createStandardJob(json task_spec) const;
    void submitStandardJob(json submission_spec) const;

    std::string addService(json service_spec) const;
    std::vector<std::string> getAllHostnames() const;

    void advanceSimulationTime(double seconds) const;

    void stopSimulation() const;

    void createAndLaunchSimulation(bool full_log,
                                   const std::string& platform_xml,
                                   const std::string& controller_host,
                                   int sleep_us);

    double getSimulationTime() const;

    bool simulation_launch_error = false;
    std::string simulation_launch_error_message;

};

#endif // WRENCH_CSSI_POC_SIMULATION_THREAD_STATE_H
