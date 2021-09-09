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
    std::shared_ptr<wrench::SimulationController> controller;
    wrench::Simulation simulation;

    ~SimulationThreadState() = default;

    void createAndLaunchSimulation(bool full_log,
                                   const std::string& platform_xml,
                                   const std::string& controller_host,
                                   int sleep_us);

    bool simulation_launch_error = false;
    std::string simulation_launch_error_message;

};

#endif // WRENCH_CSSI_POC_SIMULATION_THREAD_STATE_H
