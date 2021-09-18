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
            r = requests.post(self.daemon_url + "/startSimulation", data=json.dumps(spec))
        except Exception:
            raise WRENCHException("Cannot connect to WRENCH daemon. Perhaps it needs to be started?")

        response = r.json()
        if not response["success"]:
            self.terminated = True
            raise WRENCHException(response["failure_cause"])
        self.daemon_port = response["port_number"]
        self.daemon_url = "http://" + daemon_host + ":" + str(self.daemon_port) + "/api"

    def __del__(self):
        """
        Destructor

        :return:
        """
        if hasattr(self, "terminated") and not self.terminated:
            self.terminate()

    def terminate(self):
        """
        Terminate the simulation

        :return:
        """
        try:
            requests.post(self.daemon_url + "/terminateSimulation")
        except requests.exceptions.ConnectionError:
            pass  # The server process was killed by me!
        self.terminated = True
        return

    def wait_for_next_event(self):
        """
        Wait for the next simulation event to occur

        :return: A JSON object
        """
        r = requests.get(self.daemon_url + "/waitForNextSimulationEvent")
        response = r.json()
        return response["event"]

    def submit_standard_job(self, job_name, cs_name):
        """
        Submit a standard job to a compute service

        :param job_name: the name of the job
        :param cs_name: the name of the compute service
        :return:
        """
        submission_spec = {"job_name": job_name, "compute_service_name": cs_name}
        r = requests.post(self.daemon_url + "/submitStandardJob", data=json.dumps(submission_spec))
        response = r.json()
        if response["success"]:
            return
        else:
            raise WRENCHException(response["failure_cause"])

    def get_simulation_events(self):
        """
        Get all simulation events since last time we checked

        :return: A JSON object
        """
        r = requests.get(self.daemon_url + "/getSimulationEvents")
        response = r.json()["events"]
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
        task_spec = {"task_name": task_name, "task_flops": task_flops, "min_num_cores": min_num_cores,
                     "max_num_cores": max_num_cores}
        r = requests.post(self.daemon_url + "/createStandardJob", data=json.dumps(task_spec))

        response = r.json()
        if response["success"]:
            return StandardJob(self, response["job_id"])
        else:
            raise WRENCHException(response["failure_cause"])

    def sleep(self, seconds):
        """
        Sleep (in simulation) for a number of seconds
        :param seconds: number of seconds
        :return:
        """
        time_spec = {"increment": seconds}
        requests.post(self.daemon_url + "/addTime", data=json.dumps(time_spec))
        return

    def get_simulated_time(self):
        """
        Get the current simulation date
        :return: the simulation date
        """
        r = requests.get(self.daemon_url + "/getTime")
        response = r.json()
        return response["time"]

    def create_bare_metal_compute_service(self, hostname):
        """
        Create a bare-metal compute service

        :param hostname: name of the (simulated) host on which the compute service should run
        :return: the service name
        """
        service_spec = {"service_type": "compute_baremetal", "head_host": hostname}
        r = requests.post(self.daemon_url + "/addService", data=json.dumps(service_spec))
        response = r.json()

        if response["success"]:
            return ComputeService(self, response["compute_service_name"])
        else:
            raise WRENCHException(response["failure_cause"])

    def get_all_hostnames(self):
        """
        Get the list of hostnames in the simulated platform
        :return: list of hostnames
        """
        r = requests.get(self.daemon_url + "/getAllHostnames")
        response = r.json()
        return response["hostnames"]
