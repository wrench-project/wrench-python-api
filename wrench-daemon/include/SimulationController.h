#ifndef WORKFLOW_MANAGER_H
#define WORKFLOW_MANAGER_H

#include <wrench-dev.h>
#include <map>
#include <vector>
#include <queue>
#include <mutex>

#include <nlohmann/json.hpp>

using json = nlohmann::json;


namespace wrench {

    class SimulationController : public WMS {

    public:

        double simulationTime = 0.0;

        // Constructor
        explicit SimulationController(const std::string &hostname);

        std::string addNewService(json service_spec);

//        std::string addJob(const double& requested_duration,
//                     const unsigned int& num_nodes, const double& actual_duration);

        std::vector<std::string> getAllHostnames();
        
//        bool cancelJob(const std::string& job_name);

        void advanceSimulationTime(double seconds);

        void getEvents(std::vector<json> &events);

        double getSimulationTime();
        std::string createStandardJob(json task_spec);
        void submitStandardJob(json submission_spec);

        void stopServer();

        std::vector<std::string> getQueue();

    private:

        std::map<std::string, std::shared_ptr<ComputeService>> compute_service_registry;

        std::queue<wrench::ComputeService *> compute_services_to_start;
        std::queue< std::pair<std::shared_ptr<StandardJob>, std::shared_ptr<ComputeService>>> submissions_to_do;

        int main() override;

        std::string addNewBareMetalComputeService(json service_spec);

        /**
         * @brief Holds the job manager
         */
        std::shared_ptr<JobManager> job_manager;

        /**
         * @brief Holds the data_movement manager
         */
        std::shared_ptr<DataMovementManager> data_movement_manager;

        /**
         * @brief Flag value to determine whether an event check needs to be executed.
         */
        bool check_event = false;

        /**
         * @brief Flag value to determine if the simulation needs to end.
         */
        bool stop = false;

        /**
         * @brief Holds queue of event_queue within the simulation to allow it to pass between web wrench-daemon and simulation threads.
         */
        std::queue<std::pair<double, std::shared_ptr<wrench::WorkflowExecutionEvent>>> event_queue;

        /**
         * @brief Holds queue of jobs to cancel within the simulation to allow it to pass between web wrench-daemon and simulation threads.
         */
        std::queue<std::string> cancelJobs;

        /**
         * @brief Holds queue of completed jobs within the simulation in order to clean up
         * to allow it to pass between web wrench-daemon and simulation threads.
         */
        std::queue<std::shared_ptr<wrench::WorkflowJob>> doneJobs;

//        /**
//         * @brief Holds queue of jobs to start within the simulation to allow it to pass between web wrench-daemon and simulation threads.
//         */
//        std::queue<std::pair<std::shared_ptr<wrench::StandardJob>, std::map<std::string, std::string>>> toSubmitJobs;

        /**
         * @brief Holds map of all jobs
         */
        std::map<std::string, std::shared_ptr<wrench::StandardJob>> job_registry;

        /**
         * @brief Time horizon to reach, if any.
         */
        double time_horizon_to_reach = 0;

        std::mutex controller_mutex;


    };
}

#endif // WORKFLOW_MANAGER_H
