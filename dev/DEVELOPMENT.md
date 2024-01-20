# Guide for Developers

[last updated: 01/20/2024]

This page provides information for developers of this project who wish to augment the Python API (and typically also the REST API) to WRENCH. 

## Overall Design

![image](./overall_architecture.svg) 


A Python simulator written using the WRENCH Python (left-hand side of the
figure above) The Python API provides users with classes for simulation
objects (`Task`, `File`, `BareMetalComputeService`, `StandardJob`, etc.),
just like the C++ WRENCH API does. These objects are very thin and hold
almost no state, and in particular no simulation state. All simulation
state is held in the running WRENCH daemon (right-hand side of the
figure). These thin Python objects provide some methods, and all these methods
invoke a method of the `Simulation` class (which has some methods that can also
be invoked directory).  This class answers these methods calls by placing
REST API calls over HTTP sent to the WRENCH daemon.  These calls consists of
a *path* (or route), which includes some static and some dynamic data, and of attached
JSON dynamic data. 

The WRENCH daemon, implemented in C++, consists of two threads. The first
is the HTTP server thread, which received REST API calls over HTTP. It
defines all available routes and the specification of all expected data in
the requests and all expected data in the responses. For each route, in
invokes a particular method. Each of these methods takes in JSON data and
returns JSON data.  The second is the simulation thread. This threads is a
WRENCH simulator that is in charge of running the simulation based on
incoming REST API requests. **Only this thread can change the simulation state**. 
So when the HTTP server thread receives a request to read simulation state,
it can answer it directly. But when it receives a request that would modify
simulation state, it cannot answer it and instead needs to communicate
with the simulation thread.  This communication is via a thread-safe "work queue" data
structure. The HTTP server threads puts "please do this" work units in the work queue,
and the simulation thread retrieves these work units, does them, and replies
to the HTTP server thread that it's been done.  Note that the requests coming over
HTTP are all in text. That is, simulation objects are referred to by their names.
The WRENCH C++ API makes it possible to retrieve some simulation objects by their
names, but not all.  The WRENCH daemon just has several helper "registry"
data structures to keep track of some simulation objects by their names. 


## Steps to add a new REST API call

In the `wrench` repository:

  - Edit `tools/wrench/wrench-daemon/doc/wrench-openapi.json` to add the new path and all its specification. This file uses the [OpenAPI/Swagger standard](https://swagger.io/specification/)
  - In the above, make sure that the new path has a `operationId` field set to the name the C++ method that will be called when a request to this path is placed
  - Implement the above method in `tools/wrench/wrench-daemon/src/SimulationController.cpp`

## Steps to augment a new Python API 

In the `wrench-python-api` repository:

  - Add whatever class/method, with full docstrings, where most of the "work" is done by calling a method of the `Simulation` class
  - In `wrench/api/simulation.py`, implement the needed method(s)


## A Full Example

The simplest way to learn how to do this is to go through a complete example. Let's look at how part of the "workflow"
concept is implemented in the API. 

