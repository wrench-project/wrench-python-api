# Objective

The objective of this repo is to implement a tiny "hello world" proof-of-concept of the envisioned system architecture for the WRENCH (re-?)implementation as part of the NSF-funded CSSI grant. The key ideas are:

  - A "WRENCH daemon" process runs in the background with two threads:
    1. A simulation thread that runs the simulation
    2. A server thread that interacts passes client requests to the simulation thread an simulation state/event back to the the client
  - The client (i.e., the simulator implemented by the user) places REST API calls
    to interact with the WRENCH daemon
  - The client and the daemon as in locked-step w.r.t. the simulation clock

There are many design decisions to be made to implement the above architecture, and this permanently work-in-progress repo explores these decisions. 


