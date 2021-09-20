#include "SimulationController.h"

#include <random>
#include <iostream>
#include <utility>
#include <unistd.h>

// The timeout use when the SimulationController receives a message
// from the job manager. Can't be zero, but can be very small.
#define JOB_MANAGER_COMMUNICATION_TIMEOUT_VALUE 0.00000001

WRENCH_LOG_CATEGORY(simulation_controller, "Log category for SimulationController");

namespace wrench {

    /**
     * @brief Construct a new SimulationController object
     * 
     * @param hostname string containing the name of the host on which this service runs
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
        // Initial setup
        wrench::TerminalOutput::setThisProcessLoggingColor(TerminalOutput::COLOR_RED);
        WRENCH_INFO("Starting");
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
                    this->compute_service_registry.insert(new_service_shared_ptr->getName(), new_service_shared_ptr);
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
            double time_to_sleep = std::max<double>(0, time_horizon_to_reach - wrench::Simulation::getCurrentSimulatedDate());
            if (time_to_sleep > 0.0) {
                WRENCH_INFO("Sleeping %.2lf seconds", time_to_sleep);
                S4U_Simulation::sleep(time_to_sleep);
                while (auto event = this->waitForNextEvent(10*JOB_MANAGER_COMMUNICATION_TIMEOUT_VALUE)) {
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
     * @brief REST API Handler
     * @param data JSON input
     * @return JSON output
     * BEGIN_REST_API_DOCUMENTATION
     * {
     *   "REST_func": "advanceTime",
     *   "documentation":
     *     {
     *       "purpose": "Advances current simulated time by some number of seconds",
     *       "json_input": {
     *         "increment": ["double", "increment in seconds"]
     *       },
     *       "json_output": {
     *       }
     *     }
     * }
     * END_REST_API_DOCUMENTATION
     */
    json SimulationController::advanceTime(json data) {
        // Simply set the time_horizon_to_reach variable so that
        // the Controller will catch up to that time
        double increment_in_seconds = data["increment"];
        this->time_horizon_to_reach = Simulation::getCurrentSimulatedDate() + increment_in_seconds;
        return {};
    }

    /**
     * @brief REST API Handler
     * @param data JSON input
     * @return JSON output
     * BEGIN_REST_API_DOCUMENTATION
     * {
     *   "REST_func": "getTime",
     *   "documentation":
     *     {
     *       "purpose": "Retrieve the current simulated time",
     *       "json_input": {
     *       },
     *       "json_output": {
     *         "time": ["double", "simulation time in seconds"]
     *       }
     *     }
     * }
     * END_REST_API_DOCUMENTATION
     */
    json SimulationController::getSimulationTime(json data) {
        // This is not called by the simulation thread, but getting the
        // simulation time is fine as it doesn't change the state of the simulation

        json answer;
        answer["time"] = Simulation::getCurrentSimulatedDate();
        return answer;
    }


    /**
     * @brief Construct a json description of a workflow execution event
     * @param event workflow execution event
     * @return json description of the event
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

        event_desc["compute_service_name"] = job->getParentComputeService()->getName();
        event_desc["job_name"] = job->getName();
        event_desc["submit_date"] = job->getSubmitDate();
        event_desc["end_date"] = job->getEndDate();

        return event_desc;
    }

    /**
     * @brief REST API Handler
     * @param data JSON input
     * @return JSON output
     * BEGIN_REST_API_DOCUMENTATION
     * {
     *   "REST_func": "waitForNextSimulationEvent",
     *   "documentation":
     *     {
     *       "purpose": "Retrieve the next simulation event",
     *       "json_input": {
     *       },
     *       "json_output": {
     *         "event": ["json", "JSON event description"]
     *       }
     *     }
     * }
     * END_REST_API_DOCUMENTATION
     */
    json SimulationController::waitForNextSimulationEvent(json data) {

        // Set the time horizon to -1, to signify the "wait for next event" to the controller
        time_horizon_to_reach = -1.0;
        // Wait for and grab the next event
        std::pair<double, std::shared_ptr<wrench::WorkflowExecutionEvent>> event;
        this->event_queue.waitAndPop(event);

        // Construct the json event description
        std::shared_ptr<wrench::StandardJob> job;
        json event_desc = eventToJSON(event.first, event.second);

        // Construct the json answer
        json answer;
        answer["event"] = event_desc;

        return answer;
    }


    /**
     * @brief REST API Handler
     * @param data JSON input
     * @return JSON output
     * BEGIN_REST_API_DOCUMENTATION
     * {
     *   "REST_func": "getSimulationEvents",
     *   "documentation":
     *     {
     *       "purpose": "Retrieve all simulation events since last time we checked",
     *       "json_input": {
     *       },
     *       "json_output": {
     *         "events": ["list<json>", "List of JSON event descriptions"]
     *       }
     *     }
     * }
     * END_REST_API_DOCUMENTATION
     */
    json SimulationController::getSimulationEvents(json data) {

        // Deal with all events
        std::pair<double, std::shared_ptr<wrench::WorkflowExecutionEvent>> event;

        std::vector<json> json_events;

        while (this->event_queue.tryPop(event)) {
            json event_desc = eventToJSON(event.first, event.second);
            json_events.push_back(event_desc);
        }

        json answer;
        answer["events"] = json_events;
        return answer;
    }


    /**
     * @brief REST API Handler
     * @param data JSON input
     * @return JSON output
     * BEGIN_REST_API_DOCUMENTATION
     * {
     *   "REST_func": "getAllHostnames",
     *   "documentation":
     *     {
     *       "purpose": "Retrieve the names of all hosts in the simulated platform",
     *       "json_input": {
     *       },
     *       "json_output": {
     *         "hostnames": ["list<string>", "List of host names"]
     *       }
     *     }
     * }
     * END_REST_API_DOCUMENTATION
     */
    json SimulationController::getAllHostnames(json data) {
        std::vector<std::string> hostname_list = Simulation::getHostnameList();
        json answer = {};
        answer["hostnames"] = hostname_list;
        return answer;
    }

    /**
     * @brief REST API Handler
     * @param data JSON input
     * @return JSON output
     * BEGIN_REST_API_DOCUMENTATION
     * {
     *   "REST_func": "standardJobGetTasks",
     *   "documentation":
     *     {
     *       "purpose": "Retrieve the tasks in a standard job",
     *       "json_input": {
     *         "job_name": ["string", "The job's name"]
     *       },
     *       "json_output": {
     *         "tasks": ["list<string>", "A list of task names"]
     *       }
     *     }
     * }
     * END_REST_API_DOCUMENTATION
     */
    json SimulationController::getStandardJobTasks(json data) {
        std::shared_ptr<StandardJob> job;
        std::string job_name = data["job_name"];
        if (not job_registry.lookup(job_name, job)) {
            throw std::runtime_error("Unknown job '" + job_name + "'");
        }
        json answer;
        std::vector<std::string> task_names;
        for (const auto &t : job->getTasks()) {
            task_names.push_back(t->getID());
        }
        answer["tasks"] = task_names;
        return answer;
    }

    /**
     * @brief REST API Handler
     * @param data JSON input
     * @return JSON output
     * BEGIN_REST_API_DOCUMENTATION
     * {
     *   "REST_func": "addBareMetalComputeService",
     *   "documentation":
     *     {
     *       "purpose": "Create and start a bare-metal compute service",
     *       "json_input": {
     *         "head_host": ["string", "The service's head host"]
     *       },
     *       "json_output": {
     *         "service_name": ["string", "The new service's name"]
     *       }
     *     }
     * }
     * END_REST_API_DOCUMENTATION
     */
    json SimulationController::addBareMetalComputeService(json data) {
        std::string head_host = data["head_host"];

        // Create the new service
        auto new_service = new BareMetalComputeService(head_host, {head_host}, "", {}, {});
        // Put in in the list of services to start (this is because this method is called
        // by the server thread, and therefore, it will segfault horribly if it calls any
        // SimGrid simulation methods, e.g., to start a service)
        this->compute_services_to_start.push(new_service);

        // Return the expected answer
        json answer;
        answer["service_name"] = new_service->getName();
        return answer;
    }

    /**
     * @brief REST API Handler
     * @param data JSON input
     * @return JSON output
     * BEGIN_REST_API_DOCUMENTATION
     * {
     *   "REST_func": "createStandardJob",
     *   "documentation":
     *     {
     *       "purpose": "Create a new standard job",
     *       "json_input": {
     *         "tasks": ["list<string>", "List of task names"]
     *       },
     *       "json_output": {
     *         "job_name": ["string", "The new job's name"]
     *       }
     *     }
     * }
     * END_REST_API_DOCUMENTATION
     */
    json SimulationController::createStandardJob(json data) {

        std::vector<WorkflowTask *> tasks;

        for (auto const &name : data["tasks"]) {
            tasks.push_back(this->getWorkflow()->getTaskByID(name));
        }

        auto job = this->job_manager->createStandardJob(tasks, {});
        this->job_registry.insert(job->getName(), job);
        json answer;
        answer["job_name"] = job->getName();
        return answer;
    }

    /**
     * @brief REST API Handler
     * @param data JSON input
     * @return JSON output
     * BEGIN_REST_API_DOCUMENTATION
     * {
     *   "REST_func": "submitStandardJob",
     *   "documentation":
     *     {
     *       "purpose": "Submit a standard job for execution to a compute service",
     *       "json_input": {
     *         "job_name": ["string", "The job's name"],
     *         "compute_service_name": ["string", "The compute service's name"]
     *       },
     *       "json_output": {
     *       }
     *     }
     * }
     * END_REST_API_DOCUMENTATION
     */
    json SimulationController::submitStandardJob(json data) {

        std::string job_name = data["job_name"];
        std::string cs_name = data["compute_service_name"];

        std::shared_ptr<StandardJob> job;
        if (not this->job_registry.lookup(job_name, job)) {
            throw std::runtime_error("Unknown job " + job_name);
        }

        std::shared_ptr<ComputeService> cs;
        if (not this->compute_service_registry.lookup(cs_name, cs)) {
            throw std::runtime_error("Unknown service " + cs_name);
        }

        this->submissions_to_do.push(std::make_pair(job, cs));
        return {};
    }

    /**
     * @brief REST API Handler
     * @param data JSON input
     * @return JSON output
     * BEGIN_REST_API_DOCUMENTATION
     * {
     *   "REST_func": "createTask",
     *   "documentation":
     *     {
     *       "purpose": "Create a new task",
     *       "json_input": {
     *         "name": ["string", "The task's name"],
     *         "flops": ["double", "The task's flops"],
     *         "min_num_cores": ["double", "The task's minimum number of cores"],
     *         "max_num_cores": ["double", "The task's maximum number of cores"],
     *         "memory": ["double", "The task's memory requirement"]
     *       },
     *       "json_output": {
     *       }
     *     }
     * }
     * END_REST_API_DOCUMENTATION
     */
    json SimulationController::createTask(json data) {

        this->getWorkflow()->addTask(data["name"],
                                     data["flops"],
                                     data["min_num_cores"],
                                     data["max_num_cores"],
                                     data["memory"]);
        return json({});
    }

}

