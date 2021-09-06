#ifndef WRENCH_DAEMON_H
#define WRENCH_DAEMON_H

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


class WRENCHDaemon {

public:
    WRENCHDaemon(bool simulation_logging,
                 bool daemon_logging,
                 int port_number,
                 int sleep_us);

    void run();

private:
    bool simulation_logging;
    bool daemon_logging;
    int port_number;
    int sleep_us;

    void startSimulation(const Request& req, Response& res);
    void displayRequest(const Request &req);
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


#endif // WRENCH_DAEMON_H
