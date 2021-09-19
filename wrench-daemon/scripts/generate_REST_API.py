#!/usr/bin/env python3
import sys

REST_API_SPECIFICATION = [
    {"func": "getTime",
     "controller_method": "getSimulationTime",
     "documentation":
         {"purpose": "Retrieve the current simulated time",
          "json_input": {
          },
          "json_output": {
              "time": ["double", "simulation time in seconds (if success)"],
          }
          }
     },
    {"func": "getAllHostnames",
     "controller_method": "getAllHostnames",
     "documentation":
         {"purpose": "Retrieve the names of all hosts in the simulated platform",
          "json_input": {
          },
          "json_output": {
              "hostnames": ["list<string>", "list of hostnames"],
          }
          }
     },
    {"func": "addService",
     "controller_method": "addService",
     "documentation": {
         "purpose": "Add a new service to the simulation and start it",
         "json_input": {
            "service_type": ["string", "one of: compute_baremetal"],
             "head_host": ["string", "name of the host on which the service will run"]
         },
         "json_output": {
            "service_name": ["string", "name of the service"]
         }
     }
     },
    {"func": "advanceTime",
     "controller_method": "advanceTime",
     "documentation": {
         "purpose": "Advance the simulated time",
         "json_input": {
             "increment": ["double", "time increment in seconds"]
         },
         "json_output": {

         }
     }
     },
    {"func": "createStandardJob",
     "controller_method": "createStandardJob",
     "documentation": {
         "purpose": "Create a standard job",
         "json_input": {
             "task_name": ["string", "Name of the one task to create for this job"],
             "task_flops": ["double", "Task's flops"],
             "min_num_cores": ["double", "Minimum number of cores"],
             "max_num_cores": ["double", "Maximum number of cores"],
         },
         "json_output": {
             "job_name": ["string", "name of the job"]
         }
     }
     },
    {"func": "submitStandardJob",
     "controller_method": "submitStandardJob",
     "documentation": {
         "purpose": "Submit a standard job to a compute service",
         "json_input": {
             "job_name": ["string", "Name of the job to submit"],
             "compute_service_name": ["string", "Name of the compute service"],
         },
         "json_output": {
         }
     }
     },
    {"func": "getSimulationEvents",
     "controller_method": "getSimulationEvents",
     "documentation": {
         "purpose": "Retrieve simulation events that occurred since last time I checked. Each event is a JSON object "
                    "with a \"event_type\" name, whose value defines the rest of the object.",
         "json_input": {
         },
         "json_output": {
             "events": ["list<json object>", "List of events"],
         }
     }
     },
    {"func": "waitForNextSimulationEvent",
     "controller_method": "waitForNextSimulationEvent",
     "documentation": {
         "purpose": "Wait for and retrieve the next simulation event",
         "json_input": {
         },
         "json_output": {
             "event_type": ["string", "Event type (which determines the rest of the keys/values)"],
         }
     }
     },
    {"func": "standardJobGetNumTasks",
     "controller_method": "getStandardJobNumTasks",
     "documentation": {
         "purpose": "Retrieve the number of tasks in a job",
         "json_input": {
             "job_name": ["string", "Name of the job"]
         },
         "json_output": {
             "num_tasks": ["int", "Number of tasks in the job"],
         }
     }
     },

]


def generate_documentation_item(spec):
    documentation_string = "<hr>"
    documentation = spec["documentation"]

    documentation_string += "<h2>/api/" + spec["func"] + "</h2>\n\n"

    try:
        documentation_string += "<b>Purpose</b>: " + documentation["purpose"] + "<br><br>\n\n"
    except KeyError:
        pass

    if "json_output" in documentation:
        documentation["json_output"]["wrench_api_request_success"] = ["bool", "true if success, false if failure"]
        documentation["json_output"]["failure_cause"] = ["string", "human-readable error message (if failure)"]

    for json_io in ["input", "output"]:
        documentation_string += "<b>JSON " + json_io + ":</b> "

        try:
            json_items = documentation["json_" + json_io]
        except KeyError:
            continue

        if len(json_items) == 0:
            documentation_string += "{} (empty JSON)<br><br>\n"
            continue

        documentation_string += "<br>\n<table border=1>\n\n"
        documentation_string += "<tr><th>name/key</th><th>type</th><th>meaning</th></tr>\n"
        for item in json_items:
            documentation_string += "<tr><td style=\"padding:5px\">  \"" + item + "\"</td><td style=\"padding:5px\"> " + json_items[item][0] + "</td><td style=\"padding:5px\">" + json_items[item][1] + " </td></tr>\n"

        documentation_string += "\n\n"
        documentation_string += "</table><br>"

    return documentation_string


def generate_documentation():

    documentation = ""

    for spec in REST_API_SPECIFICATION:
        documentation += generate_documentation_item(spec)

    documentation += "<hr>\n"

    return documentation


if __name__ == "__main__":

    if len(sys.argv) <= 3:
        sys.stderr.write("Usage: " + sys.argv[0] + " <.h.in path> <.h path> [<doc file path>]\n")
        sys.exit(0)

    generated_code = ""
    for spec in REST_API_SPECIFICATION:
        generated_code += """\trequest_handlers[\"""" + spec["func"] + """\"] = [sc](json data) { return sc->""" + \
                          spec["controller_method"] + """(std::move(data)); };\n"""

    # Read source code
    try:
        source_code = open(sys.argv[1]).read()
    except IOError:
        sys.stderr.write("Can't read file " + sys.argv[1])
        sys.exit(1)

    # replace
    source_code = source_code.replace("REQUEST_HANDLER_SETUP", generated_code)

    # Write generated source code
    try:
        open(sys.argv[2], "w").write(source_code)
    except IOError:
        sys.stderr.write("Can't write file " + sys.argv[2])
        sys.exit(1)

    # Write doc file if needed
    if len(sys.argv) == 4:
        try:
            open(sys.argv[3], "w").write(generate_documentation())
        except IOError:
            sys.stderr.write("Can't write file " + sys.argv[3])
            sys.exit(1)

    sys.exit(0)

