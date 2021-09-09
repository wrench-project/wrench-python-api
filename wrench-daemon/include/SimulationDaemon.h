#ifndef SIMULATION_DAEMON_H
#define SIMULATION_DAEMON_H

#include "httplib.h"
using httplib::Request;
using httplib::Response;

#include <wrench-dev.h>
#include <map>
#include <vector>
#include <queue>
#include <mutex>

#include <nlohmann/json.hpp>

using json = nlohmann::json;


/**
 * @brief A class that implements a Simulation Daemon process (in the run() method)
 */
class SimulationDaemon {

public:
    SimulationDaemon(bool daemon_logging, int simulation_port_number,
                     SimulationThreadState *simulation_thread_state, std::thread& simulation_thread);

    void run();

private:

    httplib::Server server;

    bool daemon_logging;
    int simulation_port_number;
    SimulationThreadState *simulation_thread_state;
    std::thread& simulation_thread;

    void displayRequest(const Request &req) const;
    void terminateSimulation(const Request& req, Response& res);
    void alive(const Request& req, Response& res);
    void getTime(const Request& req, Response& res);
    void getAllHostnames(const Request& req, Response& res);
    void addTime(const Request& req, Response& res);
    void getSimulationEvents(const Request& req, Response& res);
    void waitForNextSimulationEvent(const Request &req, Response & res);
    void addService(const Request& req, Response& res);
    void submitStandardJob(const Request& req, Response& res);
    void createStandardJob(const Request& req, Response& res);

};


#endif // SIMULATION_DAEMON_H
