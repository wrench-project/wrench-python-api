#include "SimulationController.h"

#include <random>
#include <iostream>
#include <unistd.h>


WRENCH_LOG_CATEGORY(simulation_controller, "Log category for SimulationController");


namespace wrench {

    /**
     * @brief Construct a new Workflow Manager object
     * 
     * @param hostname String containing the name of the simulated computer.
     */
    SimulationController::SimulationController(
            const std::string &hostname) :
            WMS(
                    nullptr, nullptr,
                    {},
                    {},
                    {}, nullptr,
                    hostname,
                    "SimulationController"
            ) {
    }

    /**
     * @brief Simulation controller's main method
     * 
     * @return int  exit code
     */
    int SimulationController::main()
    {
        // Setup
        wrench::TerminalOutput::setThisProcessLoggingColor(TerminalOutput::COLOR_RED);
        WRENCH_INFO("Starting");
        WRENCH_INFO("Creating a Job Manager");
        this->job_manager = this->createJobManager();
        WRENCH_INFO("Creating a Data Movement Manager");
        this->data_movement_manager = this->createDataMovementManager();

        double time_origin = this->simulation->getCurrentSimulatedDate();

        // Main control loop
        while(true)
        {

            // Start compute services that should be started, if any
            while (true) {
//                WRENCH_INFO("IN SERVICE CREATION LOOP");
                wrench::ComputeService *new_compute_service = nullptr;
                controller_mutex.lock();
//                WRENCH_INFO("EMPTUY: %d", this->compute_services_to_start.empty());
                if (!this->compute_services_to_start.empty()) {
                    new_compute_service = this->compute_services_to_start.front();
                    this->compute_services_to_start.pop();
                }
                controller_mutex.unlock();
                if (new_compute_service == nullptr) break;

                // Start the new service
                auto new_service_shared_ptr = this->simulation->startNewService(new_compute_service);
                // Add the new service to the "database" of existing services, so that
                // later we can look it up by name
                this->service_registry[new_service_shared_ptr->getName()] = new_service_shared_ptr;
            }

//            // Add tasks onto the job_manager so it can begin processing them
//            while (!this->toSubmitJobs.empty())
//            {
//                // Retrieves the job to be submitted and set up needed arguments.
//                auto to_submit = this->toSubmitJobs.front();
//                auto job = std::get<0>(to_submit);
//                auto service_specific_args = std::get<1>(to_submit);
//
//                // Submit the job.
//                job_manager->submitJob(job, batch_service, service_specific_args);
//
//                // Lock the queue otherwise deadlocks might occur.
//                queue_mutex.lock();
//                this->toSubmitJobs.pop();
//                queue_mutex.unlock();
//                std::printf("Submit Server Time: %f\n", this->simulation->getCurrentSimulatedDate());
//            }
//
//            // Clean up memory by removing completed and failed jobs
//            while(not doneJobs.empty())
//                doneJobs.pop();
//
//            // Cancel jobs
//            while(not cancelJobs.empty())
//            {
//                // Retrieve compute service and job to execute job termination.
//                auto batch_service = *(this->getAvailableComputeServices<BatchComputeService>().begin());
//                auto job_name = cancelJobs.front();
//                try {
//                    batch_service->terminateJob(job_list[job_name]);
//                } catch (std::exception &e) {
//                    cerr << "EXCEPTION: " << e.what() << "\n";
//                }
//
//                // Remove from the map list of jobs
//                job_list.erase(job_name);
//
//                // Lock the queue otherwise deadlocks might occur.
//                queue_mutex.lock();
//                cancelJobs.pop();
//                queue_mutex.unlock();
//            }


            // Moves time forward for requested time while adding any completed events to a queue.
            // Needs to be done this way because waiting for next event cannot be done on another thread.

            double time_to_sleep = std::max<double>(0, time_horizon_to_reach - wrench::Simulation::getCurrentSimulatedDate());

            if (time_to_sleep > 0.0) {
                S4U_Simulation::sleep(time_to_sleep);
                // TODO: NOT SURE THIS BELOW WORKS FOR EVENTS, WOULD BE NICE (WE HAVE THE OLD CODE BELOW)
                while (auto event = this->waitForNextEvent(0.0)) {
                    std::printf("Event Server Time: %f\n", Simulation::getCurrentSimulatedDate());
                    std::printf("Event: %s\n", event->toString().c_str());
                    // Add job onto the event queue with locks to prevent deadlocks.
                    controller_mutex.lock();
                    events.push(std::make_pair(this->simulation->getCurrentSimulatedDate(), event));
                    controller_mutex.unlock();
                }
            }
#if 0
            while(this->simulationTime < time_horizon_to_reach)
            {
                // Retrieve event by going through sec increments.
                auto event = this->waitForNextEvent(0.001);
                WRENCH_INFO("TICK");
                this->simulationTime = wrench::Simulation::getCurrentSimulatedDate();

                // Checks if there was a job event during the time period
                if(event != nullptr)
                {
                    std::printf("Event Server Time: %f\n", this->simulation->getCurrentSimulatedDate());
                    std::printf("Event: %s\n", event->toString().c_str());
                    // Add job onto the event queue with locks to prevent deadlocks.
                    controller_mutex.lock();
                    events.push(std::make_pair(this->simulation->getCurrentSimulatedDate(), event));
                    controller_mutex.unlock();
                }
            }
#endif

            // Exits if wrench-daemon needs to stop
            if(stop)
                break;
            // Sleep since no matter what we're in locked step with real time and don't want
            // to burn CPU cycles like crazy. Could probably sleep 1s...
            usleep(100);
        }
        return 0;
    }

    /**
     * @brief Sets the flag to stop the wrench-daemon since the web wrench-daemon and simulation_controller wrench-daemon run on two different threads.
     */
    void SimulationController::stopServer()
    {
        stop = true;
    }


#if 0
    /**
     * @brief Adds a job to the simulation
     * 
     * @param job_name Name of job to be added (currently not in use)
     * @param requested_duration How long the job should run in seconds.
     * @param num_nodes Number of nodes requested.
     * @param actual_duration How long the job will run in seconds.
     * @return std::string Name of job or empty string if failed to create.
     */
    std::string SimulationController::addJob(const double& requested_duration,
                                             const unsigned int& num_nodes,
                                             const double &actual_duration)
    {
        static long task_id = 0;
        // Check if valid number of nodes.


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

        // Lock the queue to prevent deadlock. Put into queue due to simulation and web wrench-daemon on separate threads.
        queue_mutex.lock();
        toSubmitJobs.push(std::make_pair(job, service_specific_args));
        queue_mutex.unlock();

        // Flag that there is a job of this name created by the user needed for job cancellation. Mapping name string
        // to pointer of the job.
        job_list[job->getName()] = job;
        return job->getName();
    }
#endif

    void SimulationController::advanceSimulationTime(double seconds) {
        // Simply advance the time_horizon_to_reach variable so that
        // the Controller simply catches up
        this->time_horizon_to_reach = Simulation::getCurrentSimulatedDate() + seconds;
        WRENCH_INFO("SERVER_TIME = %lf ", this->time_horizon_to_reach);
    }

    double SimulationController::getSimulationTime() {
        // This is not called by the simulation thread, but getting the
        // simulation time is fine. It doesn't change the state of the simulation
        return Simulation::getCurrentSimulatedDate();
    }

    /**
     * @brief Retrieve the list of events for the specified time period.
     * 
     * @param statuses Queue to hold all statuses.
     * @param time Expected wrench-daemon time in seconds.
     */
    void SimulationController::getEventStatuses(std::queue<std::string>& statuses, const time_t& time)
    {
        // Keeps retrieving events while there are events and converts them to a string(temp) to return
        // to client.
        while(!events.empty())
        {
            // Locks the mutex because event statuses are in a queue shared by web wrench-daemon thread and simulation thread.
            controller_mutex.lock();
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

            controller_mutex.unlock();
        }
        time_horizon_to_reach = (double)time;
    }

    /**
     * @brief Retrieves statuses of all simulated jobs in the simulation.
     *
     * @return std::vector<std::string> List of job statuses with relevant information.
     */
    std::vector<std::string> SimulationController::getQueue()
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

    /**
     * @brief Create and start new service instance in response to a request
     * @param service_spec: a json object
     * @return the created service's name
     */
    std::string SimulationController::addNewService(json service_spec) {
        std::string service_type = service_spec["service_type"];

        if (service_type == "compute_baremetal") {
            return this->addNewBareMetalComputeService(service_spec);
        } else {
            throw std::runtime_error("Unknown service type '" + service_type + "' - cannot create it");
        }
    }

    /**
     * @brief Retrieve all hostnames
     * @return a vector of hostnames
     */
    std::vector<std::string> SimulationController::getAllHostnames() {
        return Simulation::getHostnameList();
    }


    /**
    * @brief Create new BareMetalComputeService instance in response to a request
    * @param service_spec: a json object
    * @return the created service's name
    */
    std::string SimulationController::addNewBareMetalComputeService(json service_spec) {
        std::string head_host = service_spec["head_host"];

        // Create the new service
        auto new_service = new BareMetalComputeService(head_host, {head_host}, "", {}, {});
        // Put in in the list of services to start (this is because this method is called
        // by the server thread, and therefore, it will segfault horribly if it calls any
        // SimGrid simulation methods.
        this->controller_mutex.lock();
        this->compute_services_to_start.push(new_service);
        this->controller_mutex.unlock();

        // Return the service's name
        return new_service->getName();
    }


}

