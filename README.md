[![Build][build-badge]][build-link]
[![License: LGPL v3][license-badge]](LICENSE)

<a href="https://wrench-project.org" target="_blank"><img src="https://wrench-project.org/images/logo-horizontal.png" width="350" alt="WRENCH Project" /></a>
<br/>_Cyberinfrastructure Simulation Workbench_

**UNDER DEVELOPMENT**

# Objective

The objective of this repo is to implement a tiny "hello world" proof-of-concept of the envisioned system architecture for the WRENCH (re-?)implementation as part of the NSF-funded CSSI grant. The key ideas are:

# Current Design

  - A simulation consists of a "client" (in this repo a Python client) that interacts with a "WRENCH daemon" process. 
  - The "WRENCH daemon" process, when asked to run a simulation starts a 2-thread process:
      1. A "Simulation Daemon" thread that handles all communication with the client
      2. A simulation thread that runs the WRENCH simulation
  -  The reason for the two threads is that all SimGrid calls must be placed by the same thread. So the Simulation Daemon thread, which has to acts as an HTTP server, places "please do this" requests in some thread-safe data structure that the simulation thread will then execute via WRENCH calls. 
 - The client, simulation daemon, and the simulation thread operate in locked-step w.r.t. the simulation clock.

# How to run it

  - Start the daemon: `./wrench-daemon/build/wrench-daemon` (use `--help` for all options)

  - Run the Python simulator: `./python-client-demo/simulator.py` 


[build-badge]:         https://github.com/wrench-project/wrench-api/workflows/Build/badge.svg
[build-link]:          https://github.com/wrench-project/wrench-api/actions
[license-badge]:       https://img.shields.io/badge/License-LGPL%20v3-blue.svg
