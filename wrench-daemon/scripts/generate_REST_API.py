#!/usr/bin/env python3
import sys

REST_API_SPECIFICATION = [
    {"/api/path": "getTime",
     "controller_method": "getSimulationTime",
     "documentation": """
          some documentation
          and some other
     """},
    {"/api/path": "getAllHostnames",
     "controller_method": "getAllHostnames",
     "documentation": """
          some documentation
          and some other
     """},
    {"/api/path": "addService",
     "controller_method": "addService",
     "documentation": """
          some documentation
          and some other
     """},
    {"/api/path": "advanceTime",
     "controller_method": "advanceTime",
     "documentation": """
          some documentation
          and some other
     """},
    {"/api/path": "createStandardJob",
     "controller_method": "createStandardJob",
     "documentation": """
          some documentation
          and some other
     """},
    {"/api/path": "submitStandardJob",
     "controller_method": "submitStandardJob",
     "documentation": """
          some documentation
          and some other
     """},
    {"/api/path": "getSimulationEvents",
     "controller_method": "getSimulationEvents",
     "documentation": """
          some documentation
          and some other
     """},
    {"/api/path": "waitForNextSimulationEvent",
     "controller_method": "waitForNextSimulationEvent",
     "documentation": """
          some documentation
          and some other
     """},
    {"/api/path": "standardJobGetNumTasks",
     "controller_method": "getStandardJobNumTasks",
     "documentation": """
          some documentation
          and some other
     """},

]


if __name__ == "__main__":

    if len(sys.argv) != 3:
        sys.stderr.write("Usage: " + sys.argv[0] + " <.h.in path> <.h path>\n")
        sys.exit(0)

    generated_code = ""
    for spec in REST_API_SPECIFICATION:
        generated_code += """\trequest_handlers[\"""" + spec["/api/path"] + """\"] = [sc](json data) { return sc->""" + \
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
        open(sys.argv[2], "w").write(source_code);
    except IOError:
        sys.stderr.write("Can't write file " + sys.argv[2])
        sys.exit(1)

    sys.exit(0)
