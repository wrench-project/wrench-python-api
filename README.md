[![Build][build-badge]][build-link]
[![License: LGPL v3][license-badge]](LICENSE)
![coverage-badge]


<a href="https://wrench-project.org" target="_blank"><img src="https://wrench-project.org/images/logo-horizontal.png" width="350" alt="WRENCH Project" /></a>
<br/>_Cyberinfrastructure Simulation Workbench_

# Objective

Provide a Python API for [WRENCH](https://wrench-project.org). This API is built on top of WRENCH's [REST API](https://wrench-project.org/wrench/latest/rest_api.html).

# Dependencies

  - [WRENCH](https://github.com/wrench-project/wrench) master branch and its dependencies
    - You must compile the `wrench-daemon` target (i.e., `make wrench-daemon`) during the build process before doing the usual (`sudo make install`)

# Installation

A simple `pip install .` should do. 

# Examples and Documentation

Example simulators are provided in the `examples` directory. See the `README` file therein for information on what these examples are and how to run them.  

For complete documentation, see the [API Documentation page](https://wrench-python-api.readthedocs.io/en/latest/).


[build-badge]:         https://github.com/wrench-project/wrench-python-api/actions/workflows/build.yml/badge.svg
[build-link]:          https://github.com/wrench-project/wrench-api/actions
[license-badge]:       https://img.shields.io/badge/License-LGPL%20v3-blue.svg
[coverage-badge]:     https://img.shields.io/badge/Coverage-92%25-brightgreen
