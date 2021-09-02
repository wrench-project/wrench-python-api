#include "SimulationController.h"
#include <unistd.h>
#include <nlohmann/json.hpp>



class SimulationThreadState {
public:
    std::shared_ptr<wrench::SimulationController> simulation_controller;
    wrench::Simulation simulation;

    ~SimulationThreadState() = default;

    void getEvents(std::vector<json> &events) const;

    std::string addJob(const double& requested_duration,
                       const unsigned int& num_nodes, const double& actual_duration) const;

    std::string createStandardJob(json task_spec) const;
    void submitStandardJob(json submission_spec) const;

    std::string addService(json service_spec) const;
    std::vector<std::string> getAllHostnames() const;

    void advanceSimulationTime(double seconds);

    void stopSimulation() const;

    std::vector<std::string> getQueue() const;

    void createAndLaunchSimulation(bool full_log,
                                   std::string platform_file,
                                   std::string controller_host);

    double getSimulationTime() const;
};
