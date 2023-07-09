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
import json

import requests
import pathlib

from typing import Dict, List, Optional, Union

from .compute_service import ComputeService
from .bare_metal_compute_service import BareMetalComputeService
from .cloud_compute_service import CloudComputeService
from .exception import WRENCHException
from .standard_job import StandardJob
from .storage_service import StorageService
from .file_registry_service import FileRegistryService
from .task import Task
from .file import File


class Simulation:
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

    :raises WRENCHException: if the platform file cannot be read or the daemon cannot be contacted or if there is any error in the response
    """

    def __init__(self, 
                    daemon_host: Optional[str] = "localhost",
                    daemon_port: Optional[int] = 8101
                ) -> None:
        """ Constructor """
        self.daemon_host = daemon_host
        self.daemon_port = daemon_port
        self.daemon_url = f"http://{daemon_host}:{daemon_port}/api"
        self.started = False

        # Setup atexit handler
        atexit.register(self.terminate)
        self.terminated = False
        self.spec = None

        # Simulation Item Dictionaries
        self.tasks = {}
        self.jobs = {}
        self.files = {}
        self.compute_services = {}
        self.storage_services = {}
        self.file_registry_services = {}
        # Default for test only
        self.simid = 101

    def start(self, platform_file_path: pathlib.Path,
                    controller_hostname: str) -> None:
        """
        Start a new simulation

        :param platform_file_path: path of a file that contains the simulated platform's description in XML
        :type platform_file_path: pathlib.Path
        :param controller_hostname: the name of the (simulated) host in the platform on which the simulation controller will run
        :type controller_hostname: str

        :raises WRENCHException: if there is any error during the simulation instantiation
        """
        
        if self.terminated:
            raise WRENCHException("This simulation has been terminated.")

        if not self.started:
            # Read the platform XML
            try:
                with open(platform_file_path, "r") as platform_file:
                    xml = platform_file.read()
            except Exception as e:
                raise WRENCHException(f"Cannot read platform file '{platform_file_path.absolute().name}' ({str(e)})")

            self.spec = {"platform_xml": xml, "controller_hostname": controller_hostname}
            try:
                r = requests.post(f"{self.daemon_url}/startSimulation", json=self.spec)
            except Exception:
                raise WRENCHException(f"Cannot connect to WRENCH daemon ({self.daemon_host}:{self.daemon_port}). Perhaps it needs to be started?")


            response = r.json()
            if not response["wrench_api_request_success"]:
                self.terminated = True
                raise WRENCHException(response["failure_cause"])

            self.daemon_port = response["port_number"]
            self.daemon_url = f"http://{self.daemon_host}:{self.daemon_port}/simulation"
            self.started = True
        else:
            pass

    def terminate(self) -> None:
        """
        Terminate the simulation
        """
        if not self.terminated:
            try:
                requests.post(f"{self.daemon_url}/{self.simid}/terminateSimulation", json={})
            except requests.exceptions.ConnectionError:
                pass  # The server process was just killed by me!
        self.terminated = True

    def wait_for_next_event(self) -> Dict[str, Union[str, StandardJob, ComputeService]]:
        """
        Wait for the next simulation event to occur

        :return: A JSON object
        :rtype: Dict[str, Union[str, StandardJob, ComputeService]]
        """
        r = requests.get(f"{self.daemon_url}/{self.simid}/waitForNextSimulationEvent", json={})
        # print(r.text)
        response = r.json()["event"]
        return self._json_event_to_dict(response)

    def submit_standard_job(self, job_name: str, cs_name: str) -> None:
        """
        Submit a standard job to a compute service

        :param job_name: the name of the job
        :type job_name: str
        :param cs_name: the name of the compute service
        :type cs_name: str

        :raises WRENCHException: if there is any error in the response
        """
        '''
        ToDo: we already have job_name in route, do we have to put it in json
        However, in wrench-openapi.json, job name was described as job_id - jid
        '''
        #ToDo: remove redundent field from json
        data = {"compute_service_name": cs_name}
        r = requests.post(f"{self.daemon_url}/{self.simid}/{job_name}/submit", json=data)
        response = r.json()
        if not response["wrench_api_request_success"]:
            raise WRENCHException(response["failure_cause"])

    def create_file_copy_at_storage_service(self, file_name: str, storage_service_name: str):
        """
        Create a copy (ex nihilo) of a file at a storage service

        :param file_name: the file name
        :type file_name: str
        :param storage_service_name: the name of the storage service
        :type storage_service_name: str

        :raises WRENCHException: if there is any error in the response
        """
        data = {"filename": file_name}
        r = requests.post(f"{self.daemon_url}/{self.simid}/{storage_service_name}/createFileCopy", json=data)
        response = r.json()
        if not response["wrench_api_request_success"]:
            raise WRENCHException(response["failure_cause"])


    def get_simulation_events(self) -> List[Dict[str, Union[str, StandardJob, ComputeService]]]:
        """
        Get all simulation events since last time we checked

        :return: A list of events
        :rtype: List[Dict[str, Union[str, StandardJob, ComputeService]]]
        """
        r = requests.get(f"{self.daemon_url}/{self.simid}/simulationEvents", json={})
        # print(r.text)
        # print(r.json())
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

        :raises WRENCHException: if there is any error in the response
        """
        task_names = [t.name for t in tasks]
        data = {"tasks": task_names}
        r = requests.put(f"{self.daemon_url}/{self.simid}/createStandardJob", json=data)

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

        :raises WRENCHException: if there is any error in the response
        """
        data = {"name": name,
                "flops": flops,
                "min_num_cores": min_num_cores,
                "max_num_cores": max_num_cores,
                "memory": memory}
        r = requests.put(f"{self.daemon_url}/{self.simid}/createTask", json=data)

        response = r.json()
        if response["wrench_api_request_success"]:
            self.tasks[name] = Task(self, name)
            return self.tasks[name]
        raise WRENCHException(response["failure_cause"])

    def add_file(self, name: str, size: int) -> File:
        """
        Add a file to the workflow

        :param name: file name
        :type name: str
        :param size: file size in bytes
        :type size: int

        :return: A file object
        :rtype: File

        :raises WRENCHException: if there is any error in the response
        """
        data = {"name": name, "size": size}
        r = requests.put(f"{self.daemon_url}/{self.simid}/addFile", json=data)

        response = r.json()
        print(response)
        if response["wrench_api_request_success"]:
            # print("Printing File")
            # print(File(self, name))
            print("CREATING FILE")
            self.files[name] = File(self, name)
            print("CRATED FIL")
            print("PRINTING FILE")
            print(self.files[name])
            return self.files[name]
        raise WRENCHException(response["failure_cause"])

    def add_input_file(self, task: str, file: File) -> None:
        """
        Add an input file to a task

        :param task_name: the task's name
        :type task_name: str
        :param file_name: the file's object
        :type file_name: File

        :raises WRENCHException: if there is any error in the response
        """
        data = {"task": task, "file": file.get_name()}
        r = requests.post(f"{self.daemon_url}/addInputFile", json=data)

        response = r.json()
        if not response["wrench_api_request_success"]:
            raise WRENCHException(response["failure_cause"])

    def add_output_file(self, task: str, file: File) -> None:
        """
        Add an output file to a task

        :param task_name: the task's name
        :type task_name: str
        :param file_name: the file's object
        :type file_name: File

        :raises WRENCHException: if there is any error in the response
        """
        data = {"task": task, "file": file.get_name()}
        r = requests.post(f"{self.daemon_url}/addOutputFile", json=data)

        response = r.json()
        if not response["wrench_api_request_success"]:
            raise WRENCHException(response["failure_cause"])

    def get_input_files(self) -> List[str]:
        """
        Get a list of all input files of the workflow

        :return: The list of input files
        :rtype: List[str]

        :raises WRENCHException: if there is any error in the response
        """
        r = requests.post(f"{self.daemon_url}/getInputFiles", json={})
        
        response = r.json()
        if response["wrench_api_request_success"]:
            return response["files"]
        raise WRENCHException(response["failure_cause"])

    def get_task_input_files(self, task: str) -> List[str]:
        """
        Get a list of input files for a given task

        :return: The list of input files
        :rtype: List[str]

        :raises WRENCHException: if there is any error in the response
        """
        data = {"task": task}

        r = requests.post(f"{self.daemon_url}/getTaskInputFiles", json=data)

        response = r.json()
        if response["wrench_api_request_success"]:
            return response["files"]
        raise WRENCHException(response["failure_cause"])

    def stage_files(self, storage_service: StorageService) -> None:
        """
        Stage all input files into the storage service

        :param storage_service: Storage service's name
        :type storage_service: StorageService

        :raises WRENCHException: if there is any error in the response
        """
        data = {"storage": storage_service.get_name()}

        r = requests.post(f"{self.daemon_url}/stageInputFiles", json=data)

        response = r.json()
        if not response["wrench_api_request_success"]:
            raise WRENCHException(response["failure_cause"])

    def file_get_size(self, file_name: str) -> int:
        """
        Get the number of bytes for a given file

        :param file_name: the file's name
        :type file_name: str

        :return: The size of the file in bytes
        :rtype: int

        :raises WRENCHException: if there is any error in the response
        """
        # data = {"name": file_name}
        data = {}
        print(f"IN FILE GET SIZE: {file_name}\n")
        print(f"{self.daemon_url}/{self.simid}/files/{file_name}/size")
        r = requests.get(f"{self.daemon_url}/{self.simid}/files/{file_name}/size", json=data)
        print(r)
        response = r.json()
        print(response)
        if response["wrench_api_request_success"]:
            return response["size"]
        raise WRENCHException(response["failure_cause"])


    def task_get_flops(self, task_name: str) -> float:
        """
        Get the number of flops in a task

        :param task_name: the task's name
        :type task_name: str

        :return: a number of flops
        :rtype: float

        :raises WRENCHException: if there is any error in the response
        """
        data = {}
        r = requests.get(f"{self.daemon_url}/{self.simid}/tasks/{task_name}/taskGetFlops", json=data)

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

        :raises WRENCHException: if there is any error in the response
        """
        data = {}
        r = requests.get(f"{self.daemon_url}/{self.simid}/tasks/{task_name}/taskGetMinNumCores", json=data)

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

        :raises WRENCHException: if there is any error in the response
        """
        data = {}
        r = requests.get(f"{self.daemon_url}/{self.simid}/tasks/{task_name}/taskGetMaxNumCores", json=data)

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

        :raises WRENCHException: if there is any error in the response
        """
        data = {}
        r = requests.get(f"{self.daemon_url}/{self.simid}/tasks/{task_name}/taskGetMemory", json=data)

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

        :raises WRENCHException: if there is any error in the response
        """
        data = {"job_name": job_name}
        r = requests.get(f"{self.daemon_url}/{self.simid}/jobs/{job_name}/tasks", json=data)

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
        requests.put(f"{self.daemon_url}/{self.simid}/advanceTime", json=data)

    def get_simulated_time(self) -> int:
        """
        Get the current simulation date

        :return: the simulation date
        :rtype: int
        """
        r = requests.get(f"{self.daemon_url}/{self.simid}/getTime", json={})
        response = r.json()
        return response["time"]

    def create_bare_metal_compute_service(self, hostname: str,
                                          resources: dict[str, [int, float]],
                                          scratch_space: str,
                                          property_list: dict[str, str],
                                          message_payload_list: dict[str, float]) -> ComputeService:
        """
        Create a bare metal compute service

        :param hostname: name of the (simulated) host on which the compute service should run
        :type hostname: str
        :param resources: compute resources as a dict of hostnames where values are tuples of #cores and ram in bytes
        :param scratch_space: the compute service’s scratch space’s mount point (”” means none)
        :type scratch_space: str
        :param property_list: a property list ({} means “use all defaults”)
        :type property_list: dict
        :param message_payload_list: a message payload list ({} means “use all defaults”)
        :type message_payload_list: dict
        :return: the service name
        :rtype: BareMetalComputeService

        :raises WRENCHException: if there is any error in the response
        """
        data = {"head_host": hostname, "resources": json.dumps(resources), "scratch_space": scratch_space,
                "property_list": json.dumps(property_list),
                "message_payload_list": json.dumps(message_payload_list),
                }
        r = requests.post(f"{self.daemon_url}/{self.simid}/addBareMetalComputeService", json=data)
        response = r.json()

        if response["wrench_api_request_success"]:
            compute_service_name = response["service_name"]
            self.compute_services[compute_service_name] = BareMetalComputeService(self, compute_service_name)
            return self.compute_services[compute_service_name]
        raise WRENCHException(response["failure_cause"])

    def create_cloud_compute_service(self, hostname: str,
                                     execution_host: list,
                                     scratch_space: str,
                                     property_list: dict[str, str],
                                     message_payload_list: dict[str, float]) -> ComputeService:
        """

                :param hostname: name of the (simulated) host on which the compute service should run
                :type hostname: str
                :param execution_host: compute resources as a list of hostnames
                :param scratch_space: the compute service’s scratch space’s mount point (”” means none)
                :type scratch_space: str
                :param property_list: a property list ({} means “use all defaults”)
                :type property_list: dict
                :param message_payload_list: a message payload list ({} means “use all defaults”)
                :type message_payload_list: dict
                :return: the service name
                :rtype: CloudComputeService

                :raises WRENCHException: if there is any error in the response
                """
        data = {"head_host": hostname, "resources": execution_host, "scratch_space": scratch_space,
                "property_list": json.dumps(property_list),
                "message_payload_list": json.dumps(message_payload_list)}

        r = requests.post(f"{self.daemon_url}/{self.simid}/addCloudComputeService", json=data)
        response = r.json()

        if response["wrench_api_request_success"]:
            compute_service_name = response["service_name"]
            self.compute_services[compute_service_name] = CloudComputeService(self, compute_service_name)
            return self.compute_services[compute_service_name]
        raise WRENCHException(response["failure_cause"])

    def create_vm(self,
                  service_name: str,
                  num_cores: int,
                  ram_memory: float,
                  property_list: dict[str, str],
                  message_payload_list: dict[str, float]) -> str:
        """
                :param Service_name: the name of the cloud compute service
                :type service_name: str
                :param Num_cores: the number of cores for the VM
                :type num_cores: int
                :param ram_memory: the VM’s RAM memory_manager_service capacity
                :type ram_memory: float
                :param property_list: a property list for the CloudComputeService that will run on the VM ({} means “use all defaults”)
                :type property_list: dict
                :param message_payload_list: a message payload list for the CloudComputeService that will run on the VM ({} means “use all defaults”))
                :type message_payload_list: dict
                :return: the service name
                :rtype: ComputeService

                :raises WRENCHException: if there is any error in the response
        """

        data = {"service_name": service_name, "num_cores": num_cores, "ram_memory": ram_memory,
                "property_list": json.dumps(property_list),
                "message_payload_list": json.dumps(message_payload_list)}

        r = requests.post(f"{self.daemon_url}/{self.simid}/createVM", json=data)
        response = r.json()

        if response["wrench_api_request_success"]:
            return response["vm_name"]
        raise WRENCHException(response["failure_cause"])

    def start_vm(self, service_name: str, vm_name: str) -> str:
        """
        Starts a VM the bare metal compute service associated to a vm
        :param service_name: name of the cloud compute service
        :type service_name: str
        :param vm_name: name of the vm
        :type vm_name: str
        :return: A bare metal compute service
        :rtype: BareMetalComputeService
        """
        data = {"service_name": service_name, "vm_name": vm_name}

        r = requests.post(f"{self.daemon_url}/{self.simid}/startVM", json=data)
        response = r.json()

        if response["wrench_api_request_success"]:
            mbcs_name = response["service_name"]
            self.compute_services[mbcs_name] = BareMetalComputeService(self, mbcs_name)
            return self.compute_services[mbcs_name]
        raise WRENCHException(response["failure_cause"])

    def shutdown_vm(self,
                  service_name: str,
                  vm_name: str):
        """
        Shutdowns a VM
        :param service_name: name of the cloud compute service
        :type service_name: str
        :param vm_name: name of the vm
        :type vm_name: str
        """

        data = {"service_name": service_name, "vm_name": vm_name}

        r = requests.post(f"{self.daemon_url}/{self.simid}/shutdownVM", json=data)
        response = r.json()

        if response["wrench_api_request_success"]:
            return
        raise WRENCHException(response["failure_cause"])

    def destroy_vm(self,
                    service_name: str,
                    vm_name: str):
        """
        Destroy a VM
        :param service_name: name of the cloud compute service
        :type service_name: str
        :param vm_name: name of the vm
        :type vm_name: str
        """

        data = {"service_name": service_name, "vm_name": vm_name}

        r = requests.post(f"{self.daemon_url}/{self.simid}/destroyVM", json=data)
        response = r.json()

        if response["wrench_api_request_success"]:
            return
        raise WRENCHException(response["failure_cause"])

    def create_simple_storage_service(self, hostname: str, mount_points: List[str]) -> StorageService:
        """
        Create a simple storage service

        :param hostname: name of the (simulated) host on which the storage service should run
        :type hostname: str
        :param mount_points: list of mount points (i.e., disks) that the storage service should use
        :type mount_points: List[str]
        :return: the service name
        :rtype: StorageService

        :raises WRENCHException: if there is any error in the response
        """
        data = {"head_host": hostname, "mount_points": mount_points}
        r = requests.post(f"{self.daemon_url}/{self.simid}/addSimpleStorageService", json=data)
        response = r.json()


        if response["wrench_api_request_success"]:
            storage_service_name = response["service_name"]
            self.storage_services[storage_service_name] = StorageService(self, storage_service_name)
            return self.storage_services[storage_service_name]
        raise WRENCHException(response["failure_cause"])

    def create_file_registry_service(self, hostname: str) -> FileRegistryService:
        """
        Create a file registry service

        :param hostname: name of the (simulated) host on which the file registry service should run
        :type hostname: str

        :return: the service name
        :rtype: FileRegistryService

        :raises WRENCHException: if there is any error in the response
        """
        data = {"head_host": hostname}
        r = requests.post(f"{self.daemon_url}/{self.simid}/addFileRegistryService", json=data)
        response = r.json()

        if response["wrench_api_request_success"]:
            file_registry_service_name = response["service_name"]
            self.file_registry_services[file_registry_service_name] = FileRegistryService(self, file_registry_service_name)
            return self.file_registry_services[file_registry_service_name]
        raise WRENCHException(response["failure_cause"])

    def get_all_hostnames(self) -> List[str]:
        """
        Get the list of hostnames in the simulated platform

        :return: list of hostnames
        :rtype: List[str]
        """
        r = requests.get(f"{self.daemon_url}/{self.simid}/hostnames", json={})
        response = r.json()
        return response["hostnames"]

    def supports_compound_jobs(self, cs_name: str) -> bool:
        """
        Returns true if the compute service supports compound jobs
        :return: Boolean
        """
        data = {"compute_service_name": cs_name}
        r = requests.get(f"{self.daemon_url}/{self.simid}/supportsCompoundJobs", json=data)
        response = r.json()
        return response["result"]

    def supports_pilot_jobs(self, cs_name: str) -> bool:
        """
        Returns true if the compute service supports pilot jobs
        :return: Boolean
        """
        data = {"compute_service_name": cs_name}
        r = requests.get(f"{self.daemon_url}/{self.simid}/supportsPilotJobs", json=data)
        response = r.json()
        return response["result"]

    def supports_standard_jobs(self, cs_name: str) -> bool:
        """
        Returns true if the compute service supports pilot jobs
        :return: Boolean
        """
        data = {"compute_service_name": cs_name}
        r = requests.get(f"{self.daemon_url}/{self.simid}/supportsStandardJobs", json=data)
        response = r.json()
        return response["result"]

    ###############################
    # Private methods
    ###############################

    def _json_event_to_dict(self, json_event: Dict[str, str]) -> Dict[str, Union[str, StandardJob, ComputeService]]:
        """

        :param json_event:
        :type json_event: Dict[str, str]

        :return:
        :rtype: Dict[str, Union[str, StandardJob, ComputeService]]

        :raises WRENCHException: if there is any error in the response
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
