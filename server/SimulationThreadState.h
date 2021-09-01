#include "workflow_manager.h"
#include <unistd.h>


class SimulationThreadState {
public:
    std::shared_ptr<wrench::WorkflowManager> wms;
    wrench::Simulation simulation;


    ~SimulationThreadState() {}

    void getEventStatuses(std::queue<std::string>& statuses, const time_t& time) const;

    std::string addJob(const double& requested_duration,
                       const unsigned int& num_nodes, const double& actual_duration) const;

    bool cancelJob(const std::string& job_name) const;

    void stopSimulation() const;

    std::vector<std::string> getQueue() const;

    void createAndLaunchSimulation(int main_argc, char **main_argv, int num_nodes, int num_cores,
                                          std::string tracefile_scheme);

    double getSimulationTime() const;
};
