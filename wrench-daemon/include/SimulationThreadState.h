#ifndef WRENCH_CSSI_POC_SIMULATION_THREAD_STATE_H
#define WRENCH_CSSI_POC_SIMULATION_THREAD_STATE_H

#include "SimulationController.h"
#include <unistd.h>
#include <nlohmann/json.hpp>

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

    int simulation_launch_error_code = 0;

};

#endif // WRENCH_CSSI_POC_SIMULATION_THREAD_STATE_H
