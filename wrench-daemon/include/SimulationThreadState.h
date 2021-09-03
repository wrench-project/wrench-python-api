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
                                   std::string platform_file,
                                   const std::string& controller_host,
                                   int sleep_us);

    double getSimulationTime() const;
};
