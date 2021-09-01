#include "workflow_manager.h"

#include <random>
#include <iostream>
#include <unistd.h>

WRENCH_LOG_CATEGORY(workflow_manager, "Log category for WorkflowManager");


namespace wrench {

    // Struct to hold information on tracefile jobs to be added in
    struct TraceFileJobInfo {
        int nodes;
        double flops;
        wrench::WorkflowTask* task;
    };

    /**
     * @brief Construct a new Workflow Manager object
     * 
     * @param compute_services Set of pointers representative of compute services.
     * @param storage_services Set of pointers representative of storage.
     * @param hostname String containing the name of the simulated computer.
     * @param node_count Integer value holding the number of nodes the computer has.
     * @param core_count Integer value holding the number of cores per node.
     */
    WorkflowManager::WorkflowManager(
            const std::set<std::shared_ptr<ComputeService>> &compute_services,
            const std::set<std::shared_ptr<StorageService>> &storage_services,
            const std::string &hostname,
            const int node_count,
            const int core_count) :
            node_count(node_count), core_count(core_count), WMS(
            nullptr, nullptr,
            compute_services,
            storage_services,
            {}, nullptr,
            hostname,
            "WorkflowManager"
    ) { }

    /**
     * @brief Overridden main within WMS to handle the how jobs are processed. 
     * 
     * @return int Default return value
     */
    int WorkflowManager::main()
    {
        this->job_manager = this->createJobManager();

        auto batch_service = *(this->getAvailableComputeServices<BatchComputeService>().begin());

        double time_origin = this->simulation->getCurrentSimulatedDate();
        // Main loop handling the WMS implementation.
        while(true)
        {
            // Add tasks onto the job_manager so it can begin processing them
            while (!this->toSubmitJobs.empty())
            {
                // Retrieves the job to be submitted and set up needed arguments.
                auto to_submit = this->toSubmitJobs.front();
                auto job = std::get<0>(to_submit);
                auto service_specific_args = std::get<1>(to_submit);

                // Submit the job.
                job_manager->submitJob(job, batch_service, service_specific_args);

                // Lock the queue otherwise deadlocks might occur.
                queue_mutex.lock();
                this->toSubmitJobs.pop();
                queue_mutex.unlock();
                std::printf("Submit Server Time: %f\n", this->simulation->getCurrentSimulatedDate());
            }

            // Clean up memory by removing completed and failed jobs
            while(not doneJobs.empty())
                doneJobs.pop();

            // Cancel jobs
            while(not cancelJobs.empty())
            {
                // Retrieve compute service and job to execute job termination.
                auto batch_service = *(this->getAvailableComputeServices<BatchComputeService>().begin());
                auto job_name = cancelJobs.front();
                try {
                    batch_service->terminateJob(job_list[job_name]);
                } catch (std::exception &e) {
                    cerr << "EXCEPTION: " << e.what() << "\n";
                }

                // Remove from the map list of jobs
                job_list.erase(job_name);

                // Lock the queue otherwise deadlocks might occur.
                queue_mutex.lock();
                cancelJobs.pop();
                queue_mutex.unlock();
            }


            // Moves time forward for requested time while adding any completed events to a queue.
            // Needs to be done this way because waiting for next event cannot be done on another thread.
            while(this->simulationTime < server_time)
            {
                // Retrieve event by going through sec increments.
                auto event = this->waitForNextEvent(1.0);
                WRENCH_INFO("TICK");
                this->simulationTime = wrench::Simulation::getCurrentSimulatedDate();

                // Checks if there was a job event during the time period
                if(event != nullptr)
                {
                    std::printf("Event Server Time: %f\n", this->simulation->getCurrentSimulatedDate());
                    std::printf("Event: %s\n", event->toString().c_str());
                    // Add job onto the event queue with locks to prevent deadlocks.
                    queue_mutex.lock();
                    events.push(std::make_pair(this->simulation->getCurrentSimulatedDate(), event));
                    queue_mutex.unlock();
                }
            }

            // Exits if server needs to stop
            if(stop)
                break;
            // Sleep since no matter what we're in locked step with real time and don't want
            // to burn CPU cycles like crazy. Could probably sleep 1s...
            usleep(100);
        }
        return 0;
    }

    /**
     * @brief Sets the flag to stop the server since the web server and wms server run on two different threads.
     */
    void WorkflowManager::stopServer()
    {
        stop = true;
    }

    /**
     * @brief Adds a job to the simulation
     * 
     * @param job_name Name of job to be added (currently not in use)
     * @param requested_duration How long the job should run in seconds.
     * @param num_nodes Number of nodes requested.
     * @param actual_duration How long the job will run in seconds.
     * @return std::string Name of job or empty string if failed to create.
     */
    std::string WorkflowManager::addJob(const double& requested_duration,
                                        const unsigned int& num_nodes,
                                        const double &actual_duration)
    {
        static long task_id = 0;
        // Check if valid number of nodes.
        if(num_nodes > node_count)
            return "";

//        cerr << "requested " << requested_duration << "\n";
//        cerr << "num_nodes " << num_nodes << "\n";
//        cerr << "actual " << actual_duration << "\n";


        // Create tasks and add to workflow.
        auto task = this->getWorkflow()->addTask(
                "task_" + std::to_string(task_id++), actual_duration, 1, 1, 0.0);

        // Create a job
        auto job = job_manager->createStandardJob(task, {});

        // Set up the command line arguments of slurm to submit job.
        std::map<std::string, std::string> service_specific_args;
        service_specific_args["-t"] = std::to_string(std::ceil(requested_duration/60)); // In MINUTES!
        service_specific_args["-N"] = std::to_string(num_nodes);
        service_specific_args["-c"] = std::to_string(1);
        service_specific_args["-u"] = "slurm_user";

//        WRENCH_INFO("SUBMITTING : -t = %s", service_specific_args["-t"].c_str());

        // Lock the queue to prevent deadlock. Put into queue due to simulation and web server on separate threads.
        queue_mutex.lock();
        toSubmitJobs.push(std::make_pair(job, service_specific_args));
        queue_mutex.unlock();

        // Flag that there is a job of this name created by the user needed for job cancellation. Mapping name string
        // to pointer of the job.
        job_list[job->getName()] = job;
        return job->getName();
    }

    /**
     * @brief Cancels a running or queued job in simulation
     * 
     * @param job_name Name of job to cancel.
     * @return true Successfully canceled.
     * @return false Failed to cancel whether no permission or doesn't exist.
     */
    bool WorkflowManager::cancelJob(const std::string& job_name)
    {
        // Search in hashtable for the job
        if(job_list[job_name] != nullptr)
        {
            // Insert into queue the job needed to be removed. Mutex needed due to
            // web server and simulation on different threads.
            queue_mutex.lock();
            cancelJobs.push(job_name);
            queue_mutex.unlock();
            return true;
        }
        cerr << "RETURNING FROM cancelJob\n";
        return false;
    }

    /**
     * @brief Retrieve the list of events for the specified time period.
     * 
     * @param statuses Queue to hold all statuses.
     * @param time Expected server time in seconds.
     */
    void WorkflowManager::getEventStatuses(std::queue<std::string>& statuses, const time_t& time)
    {
        // Keeps retrieving events while there are events and converts them to a string(temp) to return
        // to client.
        while(!events.empty())
        {
            // Locks the mutex because event statuses are in a queue shared by web server thread and simulation thread.
            queue_mutex.lock();
            auto event = events.front();
            std::shared_ptr<wrench::StandardJob> job;

            // Casts jobs to JobFailed or JobComplete and extracts the job pointer containing information.
            // Cleans up by pushing done/failed jobs onto a queue for main thread to clean up.
            if(auto failed = std::dynamic_pointer_cast<wrench::StandardJobFailedEvent>(event.second))
            {
                doneJobs.push(failed->standard_job);
                job = failed->standard_job;
            }
            else if(auto complete = std::dynamic_pointer_cast<wrench::StandardJobCompletedEvent>(event.second))
            {
                doneJobs.push(complete->standard_job);
                job = complete->standard_job;
            }

            // Check if jobs are ones submitted by user otherwise do not return anything to user.
            if(job_list[job->getName()])
            {
                double submit_date = job->getSubmitDate();
                double start_date = (*(job->getTasks().begin()))->getStartDate();
                double end_date = (*(job->getTasks().begin()))->getEndDate();
                if (end_date < 0) {
                    end_date =  (*(job->getTasks().begin()))->getFailureDate();
                }
                statuses.push(std::to_string(event.first) + " " + event.second->toString() + " " +
                              std::to_string(submit_date) + "|" +
                              std::to_string(start_date) + "|" +
                              std::to_string(end_date));
                job_list.erase(job->getName());
            }
            events.pop();

            queue_mutex.unlock();
        }
        server_time = (double)time;
    }

    /**
     * @brief Retrieves statuses of all simulated jobs in the simulation.
     * 
     * @return std::vector<std::string> List of job statuses with relevant information.
     */
    std::vector<std::string> WorkflowManager::getQueue()
    {
        std::vector<std::tuple<std::string,std::string,int,int,int,double,double>> i_queue;
        std::vector<std::string> queue;
        auto batch_services = this->getAvailableComputeServices<BatchComputeService>();

        // Loops through all available batch services (should only be one supposedly in this case).
        // and inserts into intermediary queue to extract the relevant information.
        for(auto const bs : batch_services)
        {
            auto bs_queue = bs->getQueue();
            i_queue.insert(i_queue.end(), bs_queue.begin(), bs_queue.end());
        }

        // Loops through intermediary queue and extracts the needed information to convert into a string
        // before finally inserting into queue which needs to be returned. Front-end will handle parsing
        // of informationi so information is passed as a comma-separated string.
        for(auto const q : i_queue) {
//            std::cerr << wrench::Simulation::getCurrentSimulatedDate() << "\n";
//            std::cerr << std::get<0>(q) + ',' + std::get<1>(q) + ',' + std::to_string(std::get<2>(q)) +
//                                         ',' + std::to_string(std::get<3>(q)) + ',' +
//                                         ',' + std::to_string(std::get<4>(q)) + ',' +
//                                         ',' + std::to_string(std::get<5>(q)) + ','
//                                          + std::to_string(std::get<6>(q)) << "\n";
            queue.push_back(std::get<0>(q) + ',' +
                            std::get<1>(q) + ',' +
                            std::to_string(std::get<2>(q)) + ',' +
                            std::to_string(std::get<4>(q)) + ',' +
                            std::to_string(std::get<6>(q)));
        }
        return queue;
    }
}

