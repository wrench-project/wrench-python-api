#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 The WRENCH Team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

import atexit
import requests
import pathlib

from typing import Dict, List, Optional

from .compute_service import ComputeService
from .exception import WRENCHException
from .standard_job import StandardJob
from .task import Task


class WRENCHSimulation:
    """
    WRENCH client class

    :param platform_file_path: path to the XML platform file
    :type platform_file_path: pathlib.Path
    :param controller_hostname: name of the simulated host on which the controller will run
    :type controller_hostname: str
    :param daemon_host: name of the host on which the WRENCH daemon is running
    :type daemon_host: str
    :param daemon_port: port number on which the WRENCH daemon is listening
    :type daemon_port: int
    """

    def __init__(self, platform_file_path: pathlib.Path,
                 controller_hostname: str,
                 daemon_host: str,
                 daemon_port: int) -> None:
        """ Constructor """
        self.daemon_url = f"http://{daemon_host}:{daemon_port}/api"

        # Read the platform XML
        try:
            with open(platform_file_path, "r") as platform_file:
                xml = platform_file.read()
        except Exception as e:
            raise WRENCHException(f"Cannot read platform file '{platform_file_path.absolute().name}' ({str(e)})")

        spec = {"platform_xml": xml, "controller_hostname": controller_hostname}
        try:
            r = requests.post(f"{self.daemon_url}/startSimulation", json=spec)
        except Exception:
            raise WRENCHException("Cannot connect to WRENCH daemon. Perhaps it needs to be started?")

        response = r.json()
        if not response["wrench_api_request_success"]:
            self.terminated = True
            raise WRENCHException(response["failure_cause"])
        self.daemon_port = response["port_number"]
        self.daemon_url = f"http://{daemon_host}:{self.daemon_port}/api"

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
        """
        if not self.terminated:
            try:
                requests.post(f"{self.daemon_url}/terminateSimulation", json={})
            except requests.exceptions.ConnectionError:
                pass  # The server process was just killed by me!
        self.terminated = True

    def wait_for_next_event(self) -> Dict[str, str]:
        """
        Wait for the next simulation event to occur

        :return: A JSON object
        :rtype: Dict[str, str]
        """
        r = requests.post(f"{self.daemon_url}/waitForNextSimulationEvent", json={})
        print(r.text)
        response = r.json()["event"]
        return self._json_event_to_dict(response)

    def submit_standard_job(self, job_name: str, cs_name: str) -> None:
        """
        Submit a standard job to a compute service

        :param job_name: the name of the job
        :type job_name: str
        :param cs_name: the name of the compute service
        :type cs_name: str
        """
        data = {"job_name": job_name, "compute_service_name": cs_name}
        r = requests.post(f"{self.daemon_url}/submitStandardJob", json=data)
        response = r.json()
        if not response["wrench_api_request_success"]:
            raise WRENCHException(response["failure_cause"])

    def get_simulation_events(self) -> List[Dict[str, str]]:
        """
        Get all simulation events since last time we checked

        :return: A list of events
        :rtype: List[Dict[str, str]]
        """
        r = requests.post(f"{self.daemon_url}/getSimulationEvents", json={})
        print(r.text)
        print(r.json())
        response = r.json()["events"]
        response = [self._json_event_to_dict(e) for e in response]
        return response

    def create_standard_job(self, tasks: List[Task]) -> StandardJob:
        """
        Create a one-task standard job

        :param tasks: list of tasks
        :type tasks: List[Task]

        :return: A StandardJob object
        :rtype: StandardJob
        """
        task_names = [t.name for t in tasks]
        data = {"tasks": task_names}
        r = requests.post(f"{self.daemon_url}/createStandardJob", json=data)

        response = r.json()
        if response["wrench_api_request_success"]:
            self.jobs[response["job_name"]] = StandardJob(self, response["job_name"])
            return self.jobs[response["job_name"]]
        raise WRENCHException(response["failure_cause"])

    def create_task(self, name: str, flops: float, min_num_cores: int, max_num_cores: int, memory: int) -> Task:
        """
        Create a one-task standard job

        :param name: task name
        :type name: str
        :param flops: number of flops
        :type flops: float
        :param min_num_cores: minimum number of cores
        :type min_num_cores: int
        :param max_num_cores: maximum number of cores
        :type max_num_cores: int
        :param memory: memory requirement in bytes
        :type memory: int

        :return: A task object
        :rtype: Task
        """
        data = {"name": name,
                "flops": flops,
                "min_num_cores": min_num_cores,
                "max_num_cores": max_num_cores,
                "memory": memory}
        r = requests.post(f"{self.daemon_url}/createTask", json=data)

        response = r.json()
        if response["wrench_api_request_success"]:
            self.tasks[name] = Task(self, name)
            return self.tasks[name]
        raise WRENCHException(response["failure_cause"])

    def task_get_flops(self, task_name: str) -> float:
        """
        Get the number of flops in a task

        :param task_name: the task's name
        :type task_name: str

        :return: a number of flops
        :rtype: float
        """
        data = {"name": task_name}
        r = requests.post(f"{self.daemon_url}/taskGetFlops", json=data)

        response = r.json()
        if response["wrench_api_request_success"]:
            return response["flops"]
        raise WRENCHException(response["failure_cause"])

    def task_get_min_num_cores(self, task_name: str) -> int:
        """
        Get the task's minimum number of required cores

        :param task_name: the task's name
        :type task_name: str

        :return: a number of cores
        :rtype: int
        """
        data = {"name": task_name}
        r = requests.post(f"{self.daemon_url}/taskGetMinNumCores", json=data)

        response = r.json()
        if response["wrench_api_request_success"]:
            return response["min_num_cores"]
        raise WRENCHException(response["failure_cause"])

    def task_get_max_num_cores(self, task_name: str) -> int:
        """
        Get the task's maximum number of required cores

        :param task_name: the task's name
        :type task_name: str

        :return: a number of cores
        :rtype: int
        """
        data = {"name": task_name}
        r = requests.post(f"{self.daemon_url}/taskGetMaxNumCores", json=data)

        response = r.json()
        if response["wrench_api_request_success"]:
            return response["max_num_cores"]
        raise WRENCHException(response["failure_cause"])

    def task_get_memory(self, task_name: str) -> int:
        """
        Get the task's memory requirement

        :param task_name: the task's name
        :type task_name: str

        :return: a memory footprint in bytes
        :rtype: int
        """
        data = {"name": task_name}
        r = requests.post(f"{self.daemon_url}/taskGetMemory", json=data)

        response = r.json()
        if response["wrench_api_request_success"]:
            return response["memory"]
        raise WRENCHException(response["failure_cause"])

    def standard_job_get_tasks(self, job_name: str) -> List[Task]:
        """
        Get the number of tasks in a standard job

        :param job_name: the job's name
        :type job_name: str

        :return: a list of task objects
        :rtype: List[Task]
        """
        data = {"job_name": job_name}
        r = requests.post(f"{self.daemon_url}/standardJobGetTasks", json=data)

        response = r.json()
        if response["wrench_api_request_success"]:
            return [self.tasks[x] for x in response["tasks"]]
        raise WRENCHException(response["failure_cause"])

    def sleep(self, seconds: int) -> None:
        """
        Sleep (in simulation) for a number of seconds

        :param seconds: number of seconds
        :type seconds: int
        """
        data = {"increment": seconds}
        requests.post(f"{self.daemon_url}/advanceTime", json=data)

    def get_simulated_time(self) -> int:
        """
        Get the current simulation date

        :return: the simulation date
        :rtype: int
        """
        r = requests.post(f"{self.daemon_url}/getTime", json={})
        response = r.json()
        return response["time"]

    def create_bare_metal_compute_service(self, hostname: str) -> ComputeService:
        """
        Create a bare-metal compute service

        :param hostname: name of the (simulated) host on which the compute service should run
        :type hostname: str

        :return: the service name
        :rtype: ComputeService
        """
        data = {"head_host": hostname}
        r = requests.post(f"{self.daemon_url}/addBareMetalComputeService", json=data)
        response = r.json()

        if response["wrench_api_request_success"]:
            compute_service_name = response["service_name"]
            self.compute_services[compute_service_name] = ComputeService(self, compute_service_name)
            return self.compute_services[compute_service_name]
        raise WRENCHException(response["failure_cause"])

    def get_all_hostnames(self) -> List[str]:
        """
        Get the list of hostnames in the simulated platform

        :return: list of hostnames
        :rtype: List[str]
        """
        r = requests.post(f"{self.daemon_url}/getAllHostnames", json={})
        response = r.json()
        return response["hostnames"]

    ###############################
    # Private methods
    ###############################

    def _json_event_to_dict(self, json_event: Dict[str, str]) -> Dict[str, str]:
        """

        :param json_event:
        :type json_event: Dict[str, str]

        :return:
        :rtype: Dict[str, str]
        """
        event_dict = {}
        if json_event["event_type"] == "job_completion":
            event_dict["event_type"] = json_event["event_type"]
            event_dict["compute_service"] = self.compute_services[json_event["compute_service_name"]]
            event_dict["submit_date"] = json_event["submit_date"]
            event_dict["end_date"] = json_event["end_date"]
            event_dict["event_date"] = json_event["event_date"]
            event_dict["job"] = self.jobs[json_event["job_name"]]
            return event_dict

        raise WRENCHException("Unknown event type " + json_event["event_type"])


def start_simulation(platform_file_path: pathlib.Path,
                     controller_hostname: str,
                     daemon_host: Optional[str] = "localhost",
                     daemon_port: Optional[int] = 8101) -> WRENCHSimulation:
    """
    Start a new simulation

    :param platform_file_path: path of a file that contains the simulated platform's description in XML
    :type platform_file_path: pathlib.Path
    :param controller_hostname: the name of the (simulated) host in the platform on which the simulation controller
                                will run
    :type controller_hostname: str
    :param daemon_host: the name of the host on which the WRENCH daemon is running
    :type daemon_host: Optional[str]
    :param daemon_port: port number on which the WRENCH daemon is listening
    :type daemon_port: Optional[int]

    :return: A WRENCHSimulation object
    :rtype: WRENCHSimulation
    """
    try:
        return WRENCHSimulation(platform_file_path, controller_hostname, daemon_host, daemon_port)
    except WRENCHException:
        raise
