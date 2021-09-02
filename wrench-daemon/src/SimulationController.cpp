#include "SimulationController.h"

#include <random>
#include <iostream>
#include <unistd.h>

#define JOB_MANAGER_COMMUNICATION_TIMEOUT_VALUE 0.00000001

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

            // Start compute compute services that should be started, if any
            while (true) {
                wrench::ComputeService *new_compute_service = nullptr;
                controller_mutex.lock();
                if (!this->compute_services_to_start.empty()) {
                    new_compute_service = this->compute_services_to_start.front();
                    this->compute_services_to_start.pop();
                }
                controller_mutex.unlock();
                if (new_compute_service == nullptr) break;

                // Start the new service
                WRENCH_INFO("Starting a new compute service...");
                auto new_service_shared_ptr = this->simulation->startNewService(new_compute_service);
                // Add the new service to the "database" of existing services, so that
                // later we can look it up by name
                this->compute_service_registry[new_service_shared_ptr->getName()] = new_service_shared_ptr;
            }

            // Submit jobs that should be submitted
            while (true) {
                std::pair<std::shared_ptr<StandardJob>, std::shared_ptr<ComputeService>> submission_to_do;
                controller_mutex.lock();
                if (this->submissions_to_do.empty()) {
                    controller_mutex.unlock();
                    break;
                } else {
                    submission_to_do = this->submissions_to_do.front();
                    this->submissions_to_do.pop();
                    controller_mutex.unlock();
                }
                // Do the submission
                WRENCH_INFO("Submitting a job...");
                this->job_manager->submitJob(submission_to_do.first, submission_to_do.second, {});
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
//                    batch_service->terminateJob(job_registry[job_name]);
//                } catch (std::exception &e) {
//                    cerr << "EXCEPTION: " << e.what() << "\n";
//                }
//
//                // Remove from the map list of jobs
//                job_registry.erase(job_name);
//
//                // Lock the queue otherwise deadlocks might occur.
//                queue_mutex.lock();
//                cancelJobs.pop();
//                queue_mutex.unlock();
//            }


            // Moves time forward for requested time while adding any completed event_queue to a queue.
            // Needs to be done this way because waiting for next event cannot be done on another thread.

            double time_to_sleep = std::max<double>(0, time_horizon_to_reach - wrench::Simulation::getCurrentSimulatedDate());

            if (time_to_sleep > 0.0) {
                WRENCH_INFO("Sleeping %.2lf seconds to catch up with the client", time_to_sleep);
                S4U_Simulation::sleep(time_to_sleep);
                while (auto event = this->waitForNextEvent(JOB_MANAGER_COMMUNICATION_TIMEOUT_VALUE)) {
                    std::printf("Event: %s\n", event->toString().c_str());
                    // Add job onto the event queue with locks to prevent deadlocks.
                    controller_mutex.lock();
                    event_queue.push(std::make_pair(Simulation::getCurrentSimulatedDate(), event));
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
                    event_queue.push(std::make_pair(this->simulation->getCurrentSimulatedDate(), event));
                    controller_mutex.unlock();
                }
            }
#endif

            // Exits if wrench-daemon needs to stop
            if(stop)
                break;
            // Sleep since no matter what we're in locked step with client time and don't want
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
        job_registry[job->getName()] = job;
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
     * @brief Retrieve the list of event_queue accumulated to date.
     * 
     * @param statuses Queue to hold all statuses.
     */
    void SimulationController::getEvents(std::vector<json> &events) {
        // Keeps retrieving event_queue while there are event_queue and converts them to a string(temp) to return
        // to client.
        controller_mutex.lock();
        while(!event_queue.empty()) {
            auto event = event_queue.front();
            std::shared_ptr<wrench::StandardJob> job;
            json event_desc;

            // Casts jobs to JobFailed or JobComplete and extracts the job pointer containing information.
            // Cleans up by pushing done/failed jobs onto a queue for main thread to clean up.
            if(auto failed = std::dynamic_pointer_cast<wrench::StandardJobFailedEvent>(event.second))
            {
//                doneJobs.push(failed->standard_job);
                event_desc["type"] = "job_failure";
                event_desc["failure_cause"] = failed->failure_cause->toString();
                job = failed->standard_job;
            }
            else if(auto complete = std::dynamic_pointer_cast<wrench::StandardJobCompletedEvent>(event.second))
            {
//                doneJobs.push(complete->standard_job);
                event_desc["type"] = "job_completion";
                job = complete->standard_job;
            }

            // Construct the event object as JSON

            event_desc["job_name"] = job->getName();
            event_desc["submit_date"] = job->getSubmitDate();
            event_desc["end_date"] = job->getEndDate();
            events.push_back(event_desc);
            job_registry.erase(job->getName());

            event_queue.pop();
        }

        controller_mutex.unlock();
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

/**
 * @brief Create a new job
 * @return
 */
    std::string SimulationController::createStandardJob(json task_spec) {
        auto task = this->getWorkflow()->addTask(task_spec["task_name"], task_spec["task_flops"], task_spec["min_num_cores"], task_spec["max_num_cores"], 0.0);
        auto job = this->job_manager->createStandardJob(task, {});
        this->controller_mutex.lock();
        this->job_registry[job->getName()] = job;
        this->controller_mutex.unlock();
        return job->getName();
    }

/**
 * @brief Submit a standard job
 */
    void SimulationController::submitStandardJob(json submission_spec) {
        std::string job_name = submission_spec["job_name"];
        std::string service_name = submission_spec["service_name"];
        if (this->job_registry.find(job_name) == this->job_registry.end()) {
            throw std::runtime_error("Unknown job " + job_name);
        }
        if (this->compute_service_registry.find(service_name) == this->compute_service_registry.end()) {
            throw std::runtime_error("Unknown service " + service_name);
        }
        this->controller_mutex.lock();
        this->submissions_to_do.push(std::make_pair(this->job_registry[job_name], this->compute_service_registry[service_name])) ;
        this->controller_mutex.unlock();

    }


}

