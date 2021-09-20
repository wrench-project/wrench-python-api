import requests
import json

from pywrench.compute_service import ComputeService
from pywrench.exception import WRENCHException
from pywrench.standard_job import StandardJob


class WRENCHSimulation:
    """
    WRENCH client class
    """

    def __init__(self, platform_file_path, controller_hostname, daemon_host, daemon_port):
        """
        Constructor

        :param platform_file_path: path to the XML platform file
        :param controller_hostname: name of the simulated host on which the controller will run
        :param daemon_host: name of the host on which the WRENCH daemon is running
        :param daemon_port: port number on which the WRENCH daemon is listening
        """
        self.daemon_url = "http://" + daemon_host + ":" + str(daemon_port) + "/api"

        # Read the platform XML
        try:
            platform_file = open(platform_file_path, "r")
            xml = platform_file.read()
            platform_file.close()
        except Exception as e:
            raise WRENCHException("Cannot read platform file '" + platform_file_path + "' (" + str(e) + ")")

        spec = {"platform_xml": xml, "controller_hostname": controller_hostname}
        try:
            r = requests.post(self.daemon_url + "/startSimulation", json=spec)
        except Exception:
            raise WRENCHException("Cannot connect to WRENCH daemon. Perhaps it needs to be started?")

        response = r.json()
        if not response["wrench_api_request_success"]:
            self.terminated = True
            raise WRENCHException(response["failure_cause"])
        self.daemon_port = response["port_number"]
        self.daemon_url = "http://" + daemon_host + ":" + str(self.daemon_port) + "/api"

        # Simulation Item Dictionaries
        self.jobs = {}
        self.compute_services = {}

    def __del__(self):
        """
        Destructor, which is necessary to avoid leaving dangling wrench-daemon processes running!

        :return:
        """

        try:
            if (not hasattr(self, "terminated")) or (not self.terminated):
                self.terminate()
        except Exception:
            # Ignore exceptions in here, since we're done anyway
            pass

    def terminate(self):
        """
        Terminate the simulation

        :return:
        """
        try:
            requests.post(self.daemon_url + "/terminateSimulation", json={})
        except requests.exceptions.ConnectionError:
            pass  # The server process was killed by me!
        self.terminated = True
        return

    def wait_for_next_event(self):
        """
        Wait for the next simulation event to occur

        :return: A JSON object
        """
        r = requests.post(self.daemon_url + "/waitForNextSimulationEvent", json={})
        print(r.text)
        response = r.json()["event"]
        return self.__json_event_to_dict(response)

    def submit_standard_job(self, job_name, cs_name):
        """
        Submit a standard job to a compute service

        :param job_name: the name of the job
        :param cs_name: the name of the compute service
        :return:
        """
        data = {"job_name": job_name, "compute_service_name": cs_name}
        r = requests.post(self.daemon_url + "/submitStandardJob", json=data)
        response = r.json()
        if response["wrench_api_request_success"]:
            return
        else:
            raise WRENCHException(response["failure_cause"])

    def get_simulation_events(self):
        """
        Get all simulation events since last time we checked

        :return: A JSON object
        """
        r = requests.post(self.daemon_url + "/getSimulationEvents", json={})
        print(r.text)
        print(r.json())
        response = r.json()["events"]
        response = [self.__json_event_to_dict(e) for e in response]
        return response

    def create_standard_job(self, task_name, task_flops, min_num_cores, max_num_cores):
        """
        Create a one-task standard job

        :param task_name: name of the task to create
        :param task_flops: task's flops
        :param min_num_cores: task's minimum number of cores
        :param max_num_cores: task's maximum number of cores
        :return:
        """
        data = {"task_name": task_name, "task_flops": task_flops, "min_num_cores": min_num_cores,
                     "max_num_cores": max_num_cores}
        r = requests.post(self.daemon_url + "/createStandardJob", json=data)

        response = r.json()
        if response["wrench_api_request_success"]:
            self.jobs[response["job_name"]] = StandardJob(self, response["job_name"])
            return self.jobs[response["job_name"]]
        else:
            raise WRENCHException(response["failure_cause"])

    def standard_job_get_num_tasks(self, job_name):
        """
        Return the number of tasks in a standard job
        """
        data = {"job_name": job_name}
        r = requests.post(self.daemon_url + "/standardJobGetNumTasks", json=data)

        print(r.text)
        response = r.json()
        print(response)
        if response["wrench_api_request_success"]:
            return response["num_tasks"]
        else:
            raise WRENCHException(response["failure_cause"])

    def sleep(self, seconds):
        """
        Sleep (in simulation) for a number of seconds
        :param seconds: number of seconds
        :return:
        """
        data = {"increment": seconds}
        requests.post(self.daemon_url + "/advanceTime", json=data)
        return

    def get_simulated_time(self):
        """
        Get the current simulation date
        :return: the simulation date
        """
        r = requests.post(self.daemon_url + "/getTime", json={})
        response = r.json()
        return response["time"]

    def create_bare_metal_compute_service(self, hostname):
        """
        Create a bare-metal compute service

        :param hostname: name of the (simulated) host on which the compute service should run
        :return: the service name
        """
        data = {"service_type": "compute_baremetal", "head_host": hostname}
        r = requests.post(self.daemon_url + "/addService", json=data)
        response = r.json()

        if response["wrench_api_request_success"]:
            compute_service_name = response["service_name"]
            self.compute_services[compute_service_name] = ComputeService(self, compute_service_name)
            return self.compute_services[compute_service_name]
        else:
            raise WRENCHException(response["failure_cause"])

    def get_all_hostnames(self):
        """
        Get the list of hostnames in the simulated platform
        :return: list of hostnames
        """
        r = requests.post(self.daemon_url + "/getAllHostnames", json={})
        response = r.json()
        return response["hostnames"]

    #
    # Private methods
    ###############################

    def __json_event_to_dict(self, json_event):
        event_dict = {}
        if json_event["event_type"] == "job_completion":
            event_dict["event_type"] = json_event["event_type"]
            event_dict["compute_service"] = self.compute_services[json_event["compute_service_name"]]
            event_dict["submit_date"] = json_event["submit_date"]
            event_dict["end_date"] = json_event["end_date"]
            event_dict["event_date"] = json_event["event_date"]
            event_dict["job"] = self.jobs[json_event["job_name"]]
        else:
            raise WRENCHException("Unknown event type " + json_event["event_type"])

        return event_dict
