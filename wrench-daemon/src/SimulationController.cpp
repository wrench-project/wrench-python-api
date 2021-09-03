#include "SimulationController.h"

#include <random>
#include <iostream>
#include <unistd.h>

#define JOB_MANAGER_COMMUNICATION_TIMEOUT_VALUE 0.00000001

WRENCH_LOG_CATEGORY(simulation_controller, "Log category for SimulationController");

namespace wrench {


    /**
     * @brief Construct a new SimulationController object
     * 
     * @param hostname String containing the name of the host on which this service runs
     */
    SimulationController::SimulationController(
            const std::string &hostname, int sleep_us) :

            WMS(
                    nullptr, nullptr,
                    {},
                    {},
                    {}, nullptr,
                    hostname,
                    "SimulationController"
            ), sleep_us(sleep_us) {
    }

    /**
     * @brief Simulation controller's main method
     * 
     * @return exit code
     */
    int SimulationController::main() {
        // Setup
        wrench::TerminalOutput::setThisProcessLoggingColor(TerminalOutput::COLOR_RED);WRENCH_INFO("Starting");
        this->job_manager = this->createJobManager();
        this->data_movement_manager = this->createDataMovementManager();

        // Main control loop
        while (keep_going) {

            // Start compute compute services that should be started, if any
            while (true) {
                wrench::ComputeService *new_compute_service = nullptr;
                if (this->compute_services_to_start.tryPop(new_compute_service)) {
                    WRENCH_INFO("Starting a new compute service...");
                    auto new_service_shared_ptr = this->simulation->startNewService(new_compute_service);
                    // Add the new service to the registry of existing services, so that later we can look it up by name
                    this->compute_service_registry[new_service_shared_ptr->getName()] = new_service_shared_ptr;
                } else {
                    break;
                }
            }

            // Submit jobs that should be submitted
            while (true) {
                std::pair<std::shared_ptr<StandardJob>, std::shared_ptr<ComputeService>> submission_to_do;
                if (this->submissions_to_do.tryPop(submission_to_do)) {
                    WRENCH_INFO("Submitting a job...");
                    this->job_manager->submitJob(submission_to_do.first, submission_to_do.second, {});
                } else {
                    break;
                }
            }

            // If the server thread is waiting for the next event to occur, just do that
            if (time_horizon_to_reach < 0) {
                time_horizon_to_reach = Simulation::getCurrentSimulatedDate();
                auto event = this->waitForNextEvent();
                this->event_queue.push(std::make_pair(Simulation::getCurrentSimulatedDate(), event));
            }

            // Moves time forward if needed (because the client has done a sleep),
            // And then add all events that occurred to the event queue
            double time_to_sleep = std::max<double>(0, time_horizon_to_reach -
                                                       wrench::Simulation::getCurrentSimulatedDate());

            if (time_to_sleep > 0.0) { WRENCH_INFO("Sleeping %.2lf seconds", time_to_sleep);
                S4U_Simulation::sleep(time_to_sleep);
                while (auto event = this->waitForNextEvent(JOB_MANAGER_COMMUNICATION_TIMEOUT_VALUE)) {
                    // Add job onto the event queue
                    event_queue.push(std::make_pair(Simulation::getCurrentSimulatedDate(), event));
                }
            }

            // Sleep since no matter what we're in locked step with client time and don't want
            // to burn CPU cycles like crazy. Could probably sleep 1s...
            usleep(sleep_us);
        }
        return 0;
    }

    /**
     * @brief Sets the flag to stop this service
     */
    void SimulationController::stopSimulation() {
        keep_going = false;
    }

    /**
     * @brief Advance the simulation time (a.k.a. sleep)
     * @param seconds number of seconds
     */
    void SimulationController::advanceSimulationTime(double seconds) {
        // Simply set the time_horizon_to_reach variable so that
        // the Controller will catch up to that time
        this->time_horizon_to_reach = Simulation::getCurrentSimulatedDate() + seconds;
    }

    /**
     * @brief Retrieve the simulation time
     * @return date in seconds
     */
    double SimulationController::getSimulationTime() {
        // This is not called by the simulation thread, but getting the
        // simulation time is fine as it doesn't change the state of the simulation
        return Simulation::getCurrentSimulatedDate();
    }


    /**
     * @brief Construct a json description of a workflow execution event
     * @param event workflow execution event
     * @return json description
     */
    json SimulationController::eventToJSON(double date, const std::shared_ptr<wrench::WorkflowExecutionEvent>& event) {
        // Construct the json event description
        std::shared_ptr<wrench::StandardJob> job;
        json event_desc;

        event_desc["event_date"] = date;
        // Deal with the different event types
        if (auto failed = std::dynamic_pointer_cast<wrench::StandardJobFailedEvent>(event)) {
            event_desc["event_type"] = "job_failure";
            event_desc["failure_cause"] = failed->failure_cause->toString();
            job = failed->standard_job;
        } else if (auto complete = std::dynamic_pointer_cast<wrench::StandardJobCompletedEvent>(event)) {
            event_desc["event_type"] = "job_completion";
            job = complete->standard_job;
        }

        event_desc["job_name"] = job->getName();
        event_desc["submit_date"] = job->getSubmitDate();
        event_desc["end_date"] = job->getEndDate();

        return event_desc;
    }

    /**
     * @brief Wait for the next event
     * @return the event
     */
    json SimulationController::waitForNextSimulationEvent() {

        // Set the time horizon to -1, to signify the "wait for next event" to the controller
        time_horizon_to_reach = -1.0;
        // Wait for and grab the next event
        std::pair<double, std::shared_ptr<wrench::WorkflowExecutionEvent>> event;
        this->event_queue.waitAndPop(event);

        // Construct the json event description
        std::shared_ptr<wrench::StandardJob> job;
        json event_desc = eventToJSON(event.first, event.second);

        // Remove the job from the event registry (this may not be a good idea, will see what semantics
        // we want the client API to show)
        {
            std::unique_lock<std::mutex> mlock(this->controller_mutex);
            job_registry.erase(event_desc["job_name"]);
        }

        return event_desc;
    }


    /**
     * @brief Retrieve the set of events that have occurred since last time we checked
     *
     * @param events A vector of events in which to put events
     */
    void SimulationController::getSimulationEvents(std::vector<json> &events) {

        // Deal with all events
        std::pair<double, std::shared_ptr<wrench::WorkflowExecutionEvent>> event;

        while (this->event_queue.tryPop(event)) {
            std::shared_ptr<wrench::StandardJob> job;
            json event_desc = eventToJSON(event.first, event.second);
            // Remove the job from the event registry (this may not be a good idea, will see what semantics
            // we want the client API to show)
            {
                std::unique_lock<std::mutex> mlock(this->controller_mutex);
                job_registry.erase(event_desc["job_name"]);
            }
        }
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
        // SimGrid simulation methods, e.g., to start a service)
        this->compute_services_to_start.push(new_service);

        // Return the service's name
        return new_service->getName();
    }


    /**
     * @brief Create a new job
     * @return a job name
     */
    std::string SimulationController::createStandardJob(json task_spec) {
        auto task = this->getWorkflow()->addTask(task_spec["task_name"],
                                                 task_spec["task_flops"],
                                                 task_spec["min_num_cores"],
                                                 task_spec["max_num_cores"],
                                                 0.0);
        auto job = this->job_manager->createStandardJob(task, {});
        {
            std::unique_lock<std::mutex> mlock(this->controller_mutex);
            this->job_registry[job->getName()] = job;
        }
        return job->getName();
    }


    /**
     * @brief Submit a standard job
     *
     * @param submission_spec Job submission specification
     */
    void SimulationController::submitStandardJob(json submission_spec) {
        std::shared_ptr<StandardJob> job;
        std::shared_ptr<ComputeService> cs;

        std::string job_name = submission_spec["job_name"];
        std::string service_name = submission_spec["service_name"];

        {
            std::unique_lock<std::mutex> mlock(this->controller_mutex);
            if (this->job_registry.find(job_name) == this->job_registry.end()) {
                throw std::runtime_error("Unknown job " + job_name);
            }
            job = this->job_registry[job_name];
        }
        {
            if (this->compute_service_registry.find(service_name) == this->compute_service_registry.end()) {
                throw std::runtime_error("Unknown service " + service_name);
            }
            cs = this->compute_service_registry[service_name];
        }

        this->submissions_to_do.push(
                std::make_pair(job, cs));
    }


}

