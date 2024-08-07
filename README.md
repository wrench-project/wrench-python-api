[![Build][build-badge]][build-link]
[![License: LGPL v3][license-badge]](LICENSE)

<a href="https://wrench-project.org" target="_blank"><img src="https://wrench-project.org/images/logo-horizontal.png" width="350" alt="WRENCH Project" /></a>
<br/>_Cyberinfrastructure Simulation Workbench_

# Objective

Provide a Python API for [WRENCH](https://wrench-project.org). This API is built on top of WRENCH's [REST API](https://wrench-project.org/wrench/latest/rest_api.html).

# Dependencies and Installation

  - [WRENCH](https://github.com/wrench-project/wrench) and its dependencies
    - You must compile/install the `wrench-daemon` target during the build process

  - Run `python3 ./setup.py install` to install the WRENCH Python API. 

# Example and API Documentation

An example simulator is provided in `example/simulator.py`, and can be executed as follows. In
a terminal start the `wrench-daemon` as:

```
wrench-daemon
```

(use `wrench-daemon --help` to see command-line options)

In another terminal, run the example simulator as:

```
python3 ./example/simulator.py
```

For complete documentation, see the [API Documentation page](https://wrench-python-api.readthedocs.io/en/latest/).


[build-badge]:         https://github.com/wrench-project/wrench-api/workflows/Build/badge.svg
[build-link]:          https://github.com/wrench-project/wrench-api/actions
[license-badge]:       https://img.shields.io/badge/License-LGPL%20v3-blue.svg
