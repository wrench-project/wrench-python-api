#include "SimulationController.h"
#include <unistd.h>
#include <nlohmann/json.hpp>



class SimulationThreadState {
public:
    std::shared_ptr<wrench::SimulationController> simulation_controller;
    wrench::Simulation simulation;

    ~SimulationThreadState() = default;

    void getEventStatuses(std::queue<std::string>& statuses, const time_t& time) const;

    std::string addJob(const double& requested_duration,
                       const unsigned int& num_nodes, const double& actual_duration) const;

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
