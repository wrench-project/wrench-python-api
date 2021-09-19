#include <utility>

#ifndef WRENCH_CSSI_POC_REST_API_H
#define WRENCH_CSSI_POC_REST_API_H

class REST_API {

public:
    REST_API(httplib::Server &server,
             std::function<void(const Request &req)> display_request_function,
             std::shared_ptr<wrench::SimulationController> &sc) :
             display_request_function(std::move(display_request_function)) {

        // Set up all request handlers
        request_handlers["getTime"] = [sc](json data) { return sc->getSimulationTime(std::move(data)); };
        request_handlers["getAllHostnames"] = [sc](json data) { return sc->getAllHostnames(std::move(data)); };
        request_handlers["addService"] = [sc](json data) { return sc->addService(std::move(data)); };
        request_handlers["advanceTime"] = [sc](json data) { return sc->advanceTime(std::move(data)); };
        request_handlers["createStandardJob"] = [sc](json data) { return sc->createStandardJob(std::move(data)); };
        request_handlers["submitStandardJob"] = [sc](json data) { return sc->submitStandardJob(std::move(data)); };
        request_handlers["getSimulationEvents"] = [sc](json data) { return sc->getSimulationEvents(std::move(data)); };
        request_handlers["waitForNextSimulationEvent"] = [sc](json data) { return sc->waitForNextSimulationEvent(std::move(data));};
        request_handlers["standardJobGetNumTasks"] = [sc](json data) { return sc->getStandardJobNumTasks(std::move(data));};

        // Set up all post request handlers
        for (auto const &spec : request_handlers) {
            server.Post(("/api/" + spec.first).c_str(),
                        [this](const Request &req, Response &res) {
                            this->genericRequestHandler(req, res);
                        });
        }
    }

    void genericRequestHandler(const Request &req, Response &res) {
        display_request_function(req);

        json answer;
        try {
            std::string api_function = req.path.substr(std::string("/api/").length());
            auto request_handler = this->request_handlers[api_function];
            answer = request_handler(json::parse(req.body));
            answer["wrench_api_request_success"] = true;
        } catch (std::exception &e) {
            answer["wrench_api_request_success"] = false;
            answer["failure_cause"] = e.what();
        }
        res.set_header("access-control-allow-origin", "*");
        res.set_content(answer.dump(), "application/json");
    }

private:
    std::map<std::string, std::function<json(json)>> request_handlers;
    std::function<void(const Request &req)> display_request_function;

};

#endif //WRENCH_CSSI_POC_REST_API_H
