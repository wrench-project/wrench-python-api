#include "httplib.h"
#include "SimulationThreadState.h"
#include "workflow_manager.h"

#include <unistd.h>

#include <cstdio>
#include <string>
#include <vector>

#include <nlohmann/json.hpp>
#include <wrench.h>


/**
 * @brief Creates and writes the XML config file to be used by wrench to configure simgrid.
 *
 * @param nodes Number of nodes to be simulated.
 * @param cores Number of cores per node to be simulated.
 */
void write_xml(int nodes, int cores)
{
    std::ofstream outputXML;
    outputXML.open("config.xml");
    outputXML << "<?xml version='1.0'?>\n";
    outputXML << "<!DOCTYPE platform SYSTEM \"http://simgrid.gforge.inria.fr/simgrid/simgrid.dtd\">\n";
    outputXML << "<platform version=\"4.1\">\n";
    outputXML << "    <zone id=\"AS0\" routing=\"Full\">\n";
    outputXML << "        <cluster id=\"cluster\" prefix=\"ComputeNode_\" suffix=\"\" radical=\"0-";
    outputXML <<  std::to_string(nodes - 1) + "\" speed=\"1f\" bw=\"125GBps\" core=\"";
    outputXML <<  std::to_string(cores) +"\" lat=\"0us\" router_id=\"router\"/>\n";
    outputXML << "        <zone id=\"AS1\" routing=\"Full\">\n";
    outputXML << "            <host id=\"WMSHost\" speed=\"1f\">\n";
    outputXML << "                <disk id=\"hard_drive\" read_bw=\"100GBps\" write_bw=\"100GBps\">\n";
    outputXML << "                  <prop id=\"size\" value=\"5000GiB\"/>\n";
    outputXML << "                  <prop id=\"mount\" value=\"/\"/>\n";
    outputXML << "                </disk>\n";
    outputXML << "            </host>\n";
    outputXML <<  "           <link id=\"fastlink\" bandwidth=\"10000000GBps\" latency=\"0ms\"/>\n";
    outputXML << "            <route src=\"WMSHost\" dst=\"WMSHost\"> <link_ctn id=\"fastlink\"/> </route>\n";
    outputXML << "        </zone>\n";
    outputXML << "        <link id=\"link\" bandwidth=\"10000000GBps\" latency=\"0ms\"/>\n";
    outputXML << "        <zoneRoute src=\"cluster\" dst=\"AS1\" gw_src=\"router\" gw_dst=\"WMSHost\">\n";
    outputXML << "            <link_ctn id=\"link\"/>\n";
    outputXML << "        </zoneRoute>\n";
    outputXML << "    </zone>\n";
    outputXML << "</platform>\n";
    outputXML.close();
}


int randInt(int min, int max) {
    return rand() % (max - min + 1) + min;
}

void appendWorkloadJob(FILE *f, int num_nodes, int min_time, int max_time, int submit_time) {
    static int id = 0;
    int run_time = randInt(min_time, max_time);
    std::string line = "";
    line += std::to_string(id++) + " "; // job id
    line += std::to_string(submit_time) + " "; // submit time
    line += "0 "; // wait time
    line += std::to_string(run_time) + " "; // run time
    line += std::to_string(num_nodes) + " "; // allocated num nodes
    line += "0 "; // cpu time used
    line += "0 "; // memory
    line += std::to_string(num_nodes) + " "; // requested num nodes
    line += std::to_string(run_time + 120) + " "; // requested time
    line += "0 "; // requested memory
    line += "0 "; // status
    line += std::to_string(1 + rand() % 20) + " "; // user_id
    fprintf(f, "%s\n", line.c_str());
}

void createRightNowWorkload(FILE *f, int num_nodes) {

    std::vector<int> job_sizes;

    if (num_nodes == 32) {
        // Space to leave: 4
        job_sizes = {7, 13, 14, 21, 26};
    } else {
        std::cerr << "No rightnow workload scheme available for " << num_nodes << " nodes\n";
        std::cerr << "You could run the ./computeRightnowJobSizes script...\n";
        exit(1);
    }

    // Generate 20 jobs that arrive at time zero
    for (int i=0; i < job_sizes.size(); i++) {
        appendWorkloadJob(f, job_sizes[i],
                          5000,
                          36000,
                          0);
    }
    for (int i=job_sizes.size(); i < 15; i++) {
        appendWorkloadJob(f, job_sizes[rand() % job_sizes.size()],
                          5000,
                          36000,
                          0);
    }
    // Generate 100 jobs that arrive later one after the other
    for (int i=0; i < 100; i++) {
        appendWorkloadJob(f, job_sizes[rand() % job_sizes.size()],
                          5000,
                          36000,
                          7200 * (i+1));
    }

}

void createBackfillingWorkload(FILE *f, int num_nodes) {

    std::vector<int> job_sizes;

    if (num_nodes != 32) {
        std::cerr << "No backfilling workload scheme available for " << num_nodes << " nodes\n";
        exit(1);
    }

    appendWorkloadJob(f, 16,10*3600,10*3600,1);
    appendWorkloadJob(f, 16,6*3600,6*3600,0);
    appendWorkloadJob(f, 32,8*3600,8*3600,0);
    appendWorkloadJob(f, 16,100*3600,100*3600,0);

}

void createChoicesWorkload(FILE *f, int num_nodes) {

    std::vector<int> job_sizes;

    if (num_nodes != 32) {
        std::cerr << "No choices workload scheme available for " << num_nodes << " nodes\n";
        exit(1);
    }

    appendWorkloadJob(f, 31,10*3600,10*3600,0);
    appendWorkloadJob(f, 30,0.5*3600,0.5*3600,0);
    appendWorkloadJob(f, 28,8*3600,8*3600,0);
//    appendWorkloadJob(f, 32,100*3600,100*3600,0);

}


void createTraceFile(std::string path, std::string scheme, int num_nodes) {
    // Create another invalid trace file
    auto trace_file  = fopen(path.c_str(), "w");
    if (scheme == "rightnow") {
        createRightNowWorkload(trace_file, num_nodes);
    } else if (scheme == "backfilling") {
        createBackfillingWorkload(trace_file, num_nodes);
    } else if (scheme == "choices") {
        createChoicesWorkload(trace_file, num_nodes);
    } else {
        throw std::invalid_argument("Unknown tracefile_scheme " + scheme);
    }
//    fprintf(trace_file, "1 0 -1 3600 -1 -1 -1 4 bogus -1\n");     // INVALID FIELD
    fclose(trace_file);

}


void SimulationThreadState::createAndLaunchSimulation(int main_argc, char **main_argv, int num_nodes, int num_cores,
                                                      std::string tracefile_scheme) {
    static bool never_called = true;

    // Make a copy of argc and argv
    int argc = main_argc;
    char **argv = (char **) calloc(main_argc, sizeof(char *));
    for (int i = 0; i < main_argc; i++) {
        argv[i] = (char *) calloc(strlen(main_argv[i]) + 1, sizeof(char));
        strcpy(argv[i], main_argv[i]);
    }


    // Let WRENCH grab its own command-line arguments, if any
    simulation.init(&argc, argv);

    // XML generated then read
    write_xml(num_nodes, num_cores);
    std::string simgrid_config = "config.xml";

    // Instantiate Simulated Platform
    simulation.instantiatePlatform(simgrid_config);


    // Generate vector containing variable number of compute nodes
    std::vector<std::string> nodes = {"ComputeNode_0"};
    for (int i = 1; i < num_nodes; ++i)
        nodes.push_back("ComputeNode_" + std::to_string(i));

    // Construct all services
    auto storage_service = simulation.add(new wrench::SimpleStorageService(
            "WMSHost", {"/"}, {{wrench::SimpleStorageServiceProperty::BUFFER_SIZE, "10000000"}}, {}));

    std::shared_ptr<wrench::BatchComputeService> batch_service;
    if (tracefile_scheme == "none") {
        batch_service = simulation.add(
                new wrench::BatchComputeService("ComputeNode_0", nodes, "",
                                                {{wrench::BatchComputeServiceProperty::BATCH_SCHEDULING_ALGORITHM, "conservative_bf"}},
                                                {}));
    } else {
        std::string path_to_tracefile = "/tmp/tracefile.swf";
        createTraceFile(path_to_tracefile, tracefile_scheme, num_nodes);
        auto foo = new wrench::BatchComputeService("ComputeNode_0", nodes, "",
                                                   {{wrench::BatchComputeServiceProperty::BATCH_SCHEDULING_ALGORITHM,    "conservative_bf"},
                                                    {wrench::BatchComputeServiceProperty::SIMULATED_WORKLOAD_TRACE_FILE, path_to_tracefile}},
                                                   {});
        batch_service = simulation.add(foo);
    }

    this->wms = simulation.add(
            new wrench::WorkflowManager({batch_service}, {storage_service}, "WMSHost", nodes.size(), num_cores));

    // Add workflow to wms
    wrench::Workflow workflow;
    this->wms->addWorkflow(&workflow);

    // Start the simulation. Currently cannot start the simulation in a different thread or else it will
    // seg fault. Most likely related to how simgrid handles threads so the web server has to started
    // on a different thread.
    simulation.launch();
}

void SimulationThreadState::getEventStatuses(queue<std::string> &statuses, const time_t &time) const {
    this->wms->getEventStatuses(statuses, time);
}

std::string SimulationThreadState::addJob(const double& requested_duration,
                                          const unsigned int& num_nodes, const double& actual_duration) const {
    return this->wms->addJob(requested_duration, num_nodes, actual_duration);
}

bool SimulationThreadState::cancelJob(const std::string& job_name) const {
    return this->wms->cancelJob(job_name);
}

void SimulationThreadState::stopSimulation() const {
    this->wms->stopServer();
}

std::vector<std::string> SimulationThreadState::getQueue() const {
    return this->wms->getQueue();
}

double SimulationThreadState::getSimulationTime() const {
    return this->wms->simulationTime;
}
