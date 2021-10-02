import requests
import json
import atexit

from pywrench.compute_service import ComputeService
from pywrench.exception import WRENCHException
from pywrench.standard_job import StandardJob
from pywrench.task import Task


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

        # Setup atexit handler
        atexit.register(self.terminate)
        self.terminated = False

        # Simulation Item Dictionaries
        self.tasks = {}
        self.jobs = {}
        self.compute_services = {}

    def terminate(self):
        """
        Terminate the simulation

        :return:
        """
        if not self.terminated:
            try:
                requests.post(self.daemon_url + "/terminateSimulation", json={})
            except requests.exceptions.ConnectionError:
                pass  # The server process was just killed by me!
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

    def create_standard_job(self, tasks):
        """
        Create a one-task standard job

        :param tasks: list of tasks
        :return: a job object
        """
        task_names = [t.name for t in tasks]
        data = {"tasks": task_names}
        r = requests.post(self.daemon_url + "/createStandardJob", json=data)

        response = r.json()
        if response["wrench_api_request_success"]:
            self.jobs[response["job_name"]] = StandardJob(self, response["job_name"])
            return self.jobs[response["job_name"]]
        else:
            raise WRENCHException(response["failure_cause"])

    def create_task(self, name, flops, min_num_cores, max_num_cores, memory):
        """
        Create a one-task standard job

        :param name: task name
        :param flops: number of flops
        :param min_num_cores: minimum number of cores
        :param max_num_cores: maximum number of cores
        :param memory: memory requirement in bytes
        :return: a task object
        """
        data = {"name": name, "flops": flops, "min_num_cores": min_num_cores, "max_num_cores": max_num_cores, "memory": memory}
        r = requests.post(self.daemon_url + "/createTask", json=data)

        response = r.json()
        if response["wrench_api_request_success"]:
            self.tasks[name] = Task(self, name)
            return self.tasks[name]
        else:
            raise WRENCHException(response["failure_cause"])

    def task_get_flops(self, task_name):
        """
        Get the number of tasks in a standard job
        :param task_name: the task's name

        :return: a number of flops
        """
        data = {"name": task_name}
        r = requests.post(self.daemon_url + "/taskGetFlops", json=data)

        response = r.json()
        if response["wrench_api_request_success"]:
            return response["flops"]
        else:
            raise WRENCHException(response["failure_cause"])

    def task_get_min_num_cores(self, task_name):
        """
        Get the number of tasks in a standard job
        :param task_name: the task's name

        :return: a number of cores
        """
        data = {"name": task_name}
        r = requests.post(self.daemon_url + "/taskGetMinNumCores", json=data)

        response = r.json()
        if response["wrench_api_request_success"]:
            return response["min_num_cores"]
        else:
            raise WRENCHException(response["failure_cause"])

    def task_get_max_num_cores(self, task_name):
        """
        Get the number of tasks in a standard job
        :param task_name: the task's name

        :return: a number of cores
        """
        data = {"name": task_name}
        r = requests.post(self.daemon_url + "/taskGetMaxNumCores", json=data)

        response = r.json()
        if response["wrench_api_request_success"]:
            return response["max_num_cores"]
        else:
            raise WRENCHException(response["failure_cause"])

    def task_get_memory(self, task_name):
        """
        Get the number of tasks in a standard job
        :param task_name: the task's name

        :return: a memory footprint in bytes
        """
        data = {"name": task_name}
        r = requests.post(self.daemon_url + "/taskGetMemory", json=data)

        response = r.json()
        if response["wrench_api_request_success"]:
            return response["memory"]
        else:
            raise WRENCHException(response["failure_cause"])


    def standard_job_get_tasks(self, job_name):
        """
        Get the number of tasks in a standard job
        :param job_name: the job's name

        :return: a list of task objects
        """
        data = {"job_name": job_name}
        r = requests.post(self.daemon_url + "/standardJobGetTasks", json=data)

        response = r.json()
        if response["wrench_api_request_success"]:
            return [self.tasks[x] for x in response["tasks"]]
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
        data = {"head_host": hostname}
        r = requests.post(self.daemon_url + "/addBareMetalComputeService", json=data)
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
