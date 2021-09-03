#ifndef WRENCH_CSSI_POC_SIMULATION_CONTROLLER_H
#define WRENCH_CSSI_POC_SIMULATION_CONTROLLER_H

#include <wrench-dev.h>
#include <map>
#include <vector>
#include <queue>
#include <mutex>

#include <nlohmann/json.hpp>

#include "BlockingQueue.h"

using json = nlohmann::json;

namespace wrench {

    class SimulationController : public WMS {

    public:

        explicit SimulationController(const std::string &hostname, int sleep_us);

        std::vector<std::string> getAllHostnames();

        std::string addNewService(json service_spec);

        std::string createStandardJob(json task_spec);
        void submitStandardJob(json submission_spec);

        double getSimulationTime();
        void advanceSimulationTime(double seconds);

        void getSimulationEvents(std::vector<json> &events);
        json waitForNextSimulationEvent();

        void stopSimulation();

    private:

        std::map<std::string, std::shared_ptr<wrench::StandardJob>> job_registry;
        std::map<std::string, std::shared_ptr<ComputeService>> compute_service_registry;


        // Thread safe queues of things for the server thread and the simulation thread to communicate
        BlockingQueue<std::pair<double, std::shared_ptr<wrench::WorkflowExecutionEvent>>> event_queue;
        BlockingQueue<wrench::ComputeService *> compute_services_to_start;
        BlockingQueue<std::pair<std::shared_ptr<StandardJob>, std::shared_ptr<ComputeService>>> submissions_to_do;

        // The two useful managers
        std::shared_ptr<JobManager> job_manager;
        std::shared_ptr<DataMovementManager> data_movement_manager;


        bool keep_going = true;
        double time_horizon_to_reach = 0;
        int sleep_us;

        std::mutex controller_mutex;

        int main() override;
        std::string addNewBareMetalComputeService(json service_spec);
        static json eventToJSON(double date, const std::shared_ptr<wrench::WorkflowExecutionEvent>& event);

    };
}

#endif // WRENCH_CSSI_POC_SIMULATION_CONTROLLER_H
