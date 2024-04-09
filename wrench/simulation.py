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
import pathlib
from typing import Dict, List, Optional, Union

import requests

from wrench.bare_metal_compute_service import BareMetalComputeService
from wrench.batch_compute_service import BatchComputeService
from wrench.cloud_compute_service import CloudComputeService
from wrench.compute_service import ComputeService
from wrench.exception import WRENCHException
from wrench.file import File
from wrench.file_registry_service import FileRegistryService
from wrench.standard_job import StandardJob
from wrench.compound_job import CompoundJob
from wrench.action import Action
from wrench.sleep_action import SleepAction
from wrench.compute_action import ComputeAction
from wrench.file_copy_action import FileCopyAction
from wrench.file_delete_action import FileDeleteAction
from wrench.file_write_action import FileWriteAction
from wrench.file_read_action import FileReadAction
from wrench.storage_service import StorageService
from wrench.task import Task
from wrench.virtual_machine import VirtualMachine
from wrench.workflow import Workflow


# noinspection GrazieInspection
class Simulation:
    """
    WRENCH Simulation class. This class implements a simulation "client" that connects to
    a local wrench-daemon that implements the WRENCH REST API (and which must be started independently).
    It provides top-level methods for instantiating and running a simulation.

    :param daemon_host: name of the host on which the WRENCH daemon is running
    :type daemon_host: str
    :param daemon_port: port number on which the WRENCH daemon is listening
    :type daemon_port: int
    """

    def __init__(self,
                 daemon_host: Optional[str] = "localhost",
                 daemon_port: Optional[int] = 8101
                 ) -> None:
        """
        Constructor
        """
        self.daemon_host = daemon_host
        self.daemon_port = daemon_port
        self.daemon_url = f"http://{daemon_host}:{daemon_port}/api"
        self.started = False

        # Setup atexit handler
        atexit.register(self.terminate)
        self.terminated = False
        self.spec = None

        # Simulation Item Dictionaries
        # self.tasks = {}
        self.actions = {}
        self.standard_jobs = {}
        self.compound_jobs = {}
        self.files = {}
        self.compute_services = {}
        self.storage_services = {}
        self.file_registry_services = {}
        # Default for test only
        self.simid = 101

    @staticmethod
    def __send_request_to_daemon(requests_method, route, json_data):
        try:
            r = requests_method(route, json=json_data)
            return r
        except Exception as e:
            raise WRENCHException("Connection to wrench-daemon severed: " + str(e) + "\n"
                                  "This could be an error on the "
                                  "wrench-daemon side (likely an uncaught maestro exception). Enable "
                                  "logging with the --simulation-logging and --daemon-logging "
                                  "command-line arguments")

    def start(self, platform_file_path: pathlib.Path,
              controller_hostname: str) -> None:
        """
        Start a new simulation

        :param platform_file_path: path of a file that contains the simulated platform's description in XML
        :type platform_file_path: pathlib.Path
        :param controller_hostname: the name of the (simulated) host in the platform on which the
               simulation controller will run
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
                raise WRENCHException(
                    f"Cannot connect to WRENCH daemon ({self.daemon_host}:{self.daemon_port})."
                    f" Perhaps it needs to be started?")

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
                requests.post(f"{self.daemon_url}/{self.simid}/terminateSimulation", {})
            except requests.exceptions.ConnectionError:
                pass  # The server process was just killed by me!
        self.terminated = True

    def wait_for_next_event(self) -> Dict[str, Union[str, StandardJob, ComputeService]]:
        """
        Wait for the next simulation event to occur

        :return: A JSON object
        :rtype: Dict[str, Union[str, StandardJob, ComputeService]]
        """
        r = self.__send_request_to_daemon(requests.get, f"{self.daemon_url}/{self.simid}/waitForNextSimulationEvent",
                                          json_data={})
        response = r.json()["event"]
        return self.__json_event_to_dict(response)

    def get_simulation_events(self) -> List[Dict[str, Union[str, StandardJob, ComputeService]]]:
        """
        Get all simulation events since last time we checked

        :return: A list of events
        :rtype: List[Dict[str, Union[str, StandardJob, ComputeService]]]
        """
        r = self.__send_request_to_daemon(requests.get, f"{self.daemon_url}/{self.simid}/simulationEvents",
                                          json_data={})
        response = r.json()["events"]
        response = [self.__json_event_to_dict(e) for e in response]
        return response

    def create_standard_job(self, tasks: List[Task], file_locations: dict[File, StorageService]) -> StandardJob:
        """
        Create a standard job

        :param tasks: list of tasks
        :type tasks: List[Task]
        :param file_locations: list of file locations
        :type file_locations: List[FileLocation]

        :return: A StandardJob object
        :rtype: StandardJob

        :raises WRENCHException: if there is any error in the response
        """

        # Check all tasks are in the same workflow
        workflow = tasks[0].get_workflow()
        for task in tasks:
            if task.get_workflow() != workflow:
                raise WRENCHException("Cannot create a standard job with tasks from different workflows")

        task_names = [t.name for t in tasks]

        file_locations_specs = {}
        for fl in file_locations:
            file_locations_specs[fl.get_name()] = file_locations[fl].get_name()

        data = {"tasks": task_names, "file_locations": file_locations_specs}
        r = self.__send_request_to_daemon(requests.put,
                                          f"{self.daemon_url}/{self.simid}/{workflow.get_name()}/createStandardJob",
                                          json_data=data)

        response = r.json()
        if response["wrench_api_request_success"]:
            self.standard_jobs[response["job_name"]] = StandardJob(self, response["job_name"], tasks)
            return self.standard_jobs[response["job_name"]]
        raise WRENCHException(response["failure_cause"])

    def create_compound_job(self, name: str) -> CompoundJob:
        """
        Create a Compound job

        :param name: Name of job
        :type name: str

        :return: A CompoundJob object
        :rtype: CompoundJob

        :raises WRENCHException: if there is any error in the response
        """

        data = {"name": name}
        r = self.__send_request_to_daemon(requests.post,
                                          f"{self.daemon_url}/{self.simid}/createCompoundJob",
                                          json_data=data)

        response = r.json()

        if response["wrench_api_request_success"]:
            self.compound_jobs[response["job_name"]] = CompoundJob(self, response["job_name"])
            return self.compound_jobs[response["job_name"]]
        raise WRENCHException(response["failure_cause"])

    def create_workflow(self) -> Workflow:
        """
        Create a workflow

        :return: A workflow object
        :rtype: Workflow
        """

        r = self.__send_request_to_daemon(requests.post,
                                          f"{self.daemon_url}/{self.simid}/createWorkflow", json_data={})
        response = r.json()
        if not response["wrench_api_request_success"]:
            self.terminated = True
            raise WRENCHException(response["failure_cause"])

        return Workflow(self, response["workflow_name"])

    def add_file(self, name: str, size: int) -> File:
        """
        Add a file to the simulation

        :param name: file name
        :type name: str
        :param size: file size in bytes
        :type size: int

        :return: A file object
        :rtype: File

        :raises WRENCHException: if there is any error in the response
        """
        data = {"name": name, "size": size}
        r = self.__send_request_to_daemon(requests.put, f"{self.daemon_url}/{self.simid}/addFile", json_data=data)

        response = r.json()
        if response["wrench_api_request_success"]:
            new_file = File(self, name)
            self.files[name] = new_file
            return new_file
        raise WRENCHException(response["failure_cause"])

    def get_all_files(self) -> dict[str, File]:
        """
        Get the list of all files

        :return: A dictionary of File objects where ta names are keys
        :rtype: dict[str, File]
        """
        return self.files

    def stage_files(self, storage_service: StorageService) -> None:
        """
        Stage all input files at a storage service

        :param storage_service: Storage service's name
        :type storage_service: StorageService

        :raises WRENCHException: if there is any error in the response
        """
        data = {"storage": storage_service.get_name()}

        r = self.__send_request_to_daemon(requests.post, f"{self.daemon_url}/stageInputFiles", json_data=data)

        response = r.json()
        if not response["wrench_api_request_success"]:
            raise WRENCHException(response["failure_cause"])

    def sleep(self, seconds: float) -> None:
        """
        Sleep (in simulation) for a number of seconds

        :param seconds: number of seconds
        :type seconds: float
        """
        data = {"increment": seconds}
        self.__send_request_to_daemon(requests.put, f"{self.daemon_url}/{self.simid}/advanceTime", json_data=data)

    def get_simulated_time(self) -> float:
        """
        Get the current simulation date
        :return: the simulation date
        :rtype: float
        """
        r = self.__send_request_to_daemon(requests.get, f"{self.daemon_url}/{self.simid}/getTime", {})

        response = r.json()
        return response["time"]

    def create_bare_metal_compute_service(self, hostname: str,
                                          resources: dict[str, [int, float]],
                                          scratch_space: str,
                                          property_list: dict[str, str],
                                          message_payload_list: dict[str, float]) -> BareMetalComputeService:
        """
        Create a bare metal compute service

        :param hostname: name of the (simulated) host on which the compute service should run
        :type hostname: str
        :param resources: compute resources as a dict of hostnames where values are tuples of #cores and ram in bytes
        :param scratch_space: the compute service's scratch space’s mount point ("" means none)
        :type scratch_space: str
        :param property_list: a property list ({} means "use all defaults")
        :type property_list: dict
        :param message_payload_list: a message payload list ({} means "use all defaults")
        :type message_payload_list: dict
        :return: the service name
        :rtype: BareMetalComputeService

        :raises WRENCHException: if there is any error in the response
        """
        data = {"head_host": hostname, "resources": json.dumps(resources), "scratch_space": scratch_space,
                "property_list": json.dumps(property_list),
                "message_payload_list": json.dumps(message_payload_list),
                }
        r = self.__send_request_to_daemon(requests.post,
                                          f"{self.daemon_url}/{self.simid}/addBareMetalComputeService", json_data=data)
        response = r.json()

        if response["wrench_api_request_success"]:
            compute_service_name = response["service_name"]
            self.compute_services[compute_service_name] = BareMetalComputeService(self, compute_service_name)
            return self.compute_services[compute_service_name]
        raise WRENCHException(response["failure_cause"])

    def create_batch_compute_service(self, hostname: str,
                                     resources: list,
                                     scratch_space: str,
                                     property_list: dict[str, str],
                                     message_payload_list: dict[str, float]) -> BatchComputeService:
        """
        Create a batch compute service

        :param hostname: name of the (simulated) host on which the compute service should run
        :type hostname: str
        :param resources: compute resources as a list of hostnames
        :param scratch_space: the compute service's scratch space's mount point ("" means none)
        :type scratch_space: str
        :param property_list: a property list ({} means “use all defaults”)
        :type property_list: dict
        :param message_payload_list: a message payload list ({} means “use all defaults”)
        :type message_payload_list: dict
        :return: the service name
        :rtype: BatchComputeService

        :raise WRENCHException: if there is any error in the response
        """
        data = {"head_host": hostname, "resources": resources, "scratch_space": scratch_space,
                "property_list": json.dumps(property_list),
                "message_payload_list": json.dumps(message_payload_list),
                }
        r = self.__send_request_to_daemon(requests.post,
                                          f"{self.daemon_url}/{self.simid}/addBatchComputeService", json_data=data)
        response = r.json()

        if response["wrench_api_request_success"]:
            compute_service_name = response["service_name"]
            self.compute_services[compute_service_name] = BatchComputeService(self, compute_service_name)
            return self.compute_services[compute_service_name]
        raise WRENCHException(response["failure_cause"])

    def create_cloud_compute_service(self, hostname: str,
                                     execution_host: list,
                                     scratch_space: str,
                                     property_list: dict[str, str],
                                     message_payload_list: dict[str, float]) -> CloudComputeService:
        """
        Create a cloud compute service

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

        :raise WRENCHException: if there is any error in the response
        """
        data = {"head_host": hostname, "resources": execution_host, "scratch_space": scratch_space,
                "property_list": json.dumps(property_list),
                "message_payload_list": json.dumps(message_payload_list)}

        r = self.__send_request_to_daemon(requests.post, f"{self.daemon_url}/{self.simid}/addCloudComputeService",
                                          json_data=data)
        response = r.json()

        if response["wrench_api_request_success"]:
            compute_service_name = response["service_name"]
            self.compute_services[compute_service_name] = CloudComputeService(self, compute_service_name)
            return self.compute_services[compute_service_name]
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
        r = self.__send_request_to_daemon(requests.post, f"{self.daemon_url}/{self.simid}/addSimpleStorageService",
                                          json_data=data)
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
        r = self.__send_request_to_daemon(requests.post, f"{self.daemon_url}/{self.simid}/addFileRegistryService",
                                          json_data=data)
        response = r.json()

        if response["wrench_api_request_success"]:
            file_registry_service_name = response["service_name"]
            self.file_registry_services[file_registry_service_name] = FileRegistryService(self,
                                                                                          file_registry_service_name)
            return self.file_registry_services[file_registry_service_name]
        raise WRENCHException(response["failure_cause"])

    def get_all_hostnames(self) -> List[str]:
        """
        Get the list of hostnames in the simulated platform

        :return: list of hostnames
        :rtype: List[str]
        """
        r = self.__send_request_to_daemon(requests.get, f"{self.daemon_url}/{self.simid}/hostnames", json_data={})
        response = r.json()
        return response["hostnames"]

    def create_workflow_from_json(self, json_object: json, reference_flop_rate: str, ignore_machine_specs: bool,
                                  redundant_dependencies: bool, ignore_cycle_creating_dependencies: bool,
                                  min_cores_per_task: float, max_cores_per_task: float, enforce_num_cores: bool,
                                  ignore_avg_cpu: bool, show_warnings: bool) -> Workflow:
        """
        Create a workflow from a JSON file

        :param json_object: A JSON object created from a WfCommons JSON file
        :type json_object: json
        :param reference_flop_rate: reference flop rate (e.g., "100Mf")
        :type reference_flop_rate: str
        :param ignore_machine_specs: whether to ignore machine specifications in the JSON
        :type ignore_machine_specs: bool
        :param redundant_dependencies: whether to take into account redundant task dependencies
        :type redundant_dependencies: bool
        :param ignore_cycle_creating_dependencies: whether to ignore cycles when creating task dependencies
        :type ignore_cycle_creating_dependencies: bool
        :param min_cores_per_task: the minimum cores for a task if not specified in the JSON
        :type min_cores_per_task: float
        :param max_cores_per_task: the maximum cores for a task if not specified in the JSON
        :type max_cores_per_task: float
        :param enforce_num_cores: whether to enforce the number of cores for a task even if specified in the JSON
        :type enforce_num_cores: bool
        :param ignore_avg_cpu: whether to ignore the average CPU time information in the JSON to compute
               sequential task execution times
        :type ignore_avg_cpu: bool
        :param show_warnings: whether to show warnings when importing the JSON (displayed on the wrench-daemon console)
        :type show_warnings: bool

        :return: A workflow
        :rtype: Workflow
        """

        data = {"json_string": json.dumps(json_object),
                "reference_flop_rate": reference_flop_rate,
                "ignore_machine_specs": ignore_machine_specs,
                "redundant_dependencies": redundant_dependencies,
                "ignore_cycle_creating_dependencies": ignore_cycle_creating_dependencies,
                "min_cores_per_task": min_cores_per_task,
                "max_cores_per_task": max_cores_per_task,
                "enforce_num_cores": enforce_num_cores,
                "ignore_avg_cpu": ignore_avg_cpu,
                "show_warnings": show_warnings}

        r = self.__send_request_to_daemon(requests.post, f"{self.daemon_url}/{self.simid}/createWorkflowFromJSON",
                                          json_data=data)
        response = r.json()
        # Create the workflow
        workflow = Workflow(self, response["workflow_name"])
        # Create the tasks
        for task_name in response["tasks"]:
            workflow.tasks[task_name] = Task(self, workflow, task_name)
        return workflow

    ####################################################################################
    ####################################################################################
    # Below are "private/protected" methods that are not part of the user API, but called by
    # the wrapper classes that form the user API
    ####################################################################################
    ####################################################################################

    def _submit_standard_job(self, job: StandardJob, cs: ComputeService, service_specific_args="{}") -> None:
        """
        Submit a standard job to a compute service

        :param job: the job
        :type job: StandardJob
        :param cs: the compute service
        :type cs: ComputeService

        :raises WRENCHException: if there is any error in the response
        """
        data = {"compute_service_name": cs.get_name(), "service_specific_args": service_specific_args}
        r = self.__send_request_to_daemon(requests.post, f"{self.daemon_url}/{self.simid}/"
                                                         f"standardJobs/{job.get_name()}/submit", json_data=data)
        response = r.json()
        if not response["wrench_api_request_success"]:
            raise WRENCHException(response["failure_cause"])

    def _submit_compound_job(self, job: CompoundJob, cs: ComputeService, service_specific_args="{}") -> None:
        """
        Submit a compound job to a compute service

        :param job: the job
        :type job: CompoundJob
        :param cs: the compute service
        :type cs: ComputeService

        :raises WRENCHException: if there is any error in the response
        """
        data = {"compute_service_name": cs.get_name(), "service_specific_args": service_specific_args}
        r = self.__send_request_to_daemon(requests.post, f"{self.daemon_url}/{self.simid}/"
                                                         f"compoundJobs/{job.get_name()}/submit", json_data=data)
        response = r.json()
        if not response["wrench_api_request_success"]:
            raise WRENCHException(response["failure_cause"])

    def _create_file_copy_at_storage_service(self, file: File, storage_service: StorageService):
        """
        Create a copy (ex nihilo) of a file at a storage service

        :param file: File
        :type file: the file
        :param storage_service: the storage service
        :type storage_service: StorageService

        :raises WRENCHException: if there is any error in the response
        """
        data = {"filename": file.get_name()}
        r = self.__send_request_to_daemon(requests.post,
                                          f"{self.daemon_url}/{self.simid}/"
                                          f"{storage_service.get_name()}/createFileCopy", json_data=data)
        response = r.json()
        if not response["wrench_api_request_success"]:
            raise WRENCHException(response["failure_cause"])

    def _lookup_file_at_storage_service(self, file: File, storage_service: StorageService) -> bool:
        """
        Checks whether a copy of a file is stored at a storage service

        :param file: File
        :type file: the file
        :param storage_service: the storage service
        :type storage_service: StorageService

        :return: True or false
        :rtype: bool

        :raises WRENCHException: if there is any error in the response
        """
        data = {"filename": file.get_name()}
        r = self.__send_request_to_daemon(requests.post,
                                          f"{self.daemon_url}/{self.simid}/"
                                          f"{storage_service.get_name()}/lookupFile", json_data=data)
        response = r.json()
        if not response["wrench_api_request_success"]:
            raise WRENCHException(response["failure_cause"])
        return response["result"]

    def _add_input_file(self, task: Task, file: File) -> None:
        """
        Add an input file to a task

        :param task: the task
        :type task: Task
        :param file: the file
        :type file: File

        :raises WRENCHException: if there is any error in the response
        """
        data = {"file": file.get_name()}
        r = self.__send_request_to_daemon(requests.put,
                                          f"{self.daemon_url}/{self.simid}/"
                                          f"{task.get_workflow().get_name()}/tasks/"
                                          f"{task.get_name()}/addInputFile", json_data=data)

        response = r.json()
        if not response["wrench_api_request_success"]:
            raise WRENCHException(response["failure_cause"])

    def _add_output_file(self, task: Task, file: File) -> None:
        """
        Add an output file to a task

        :param task: the task
        :type task: Task
        :param file: the file
        :type file: File

        :raises WRENCHException: if there is any error in the response
        """
        data = {"file": file.get_name()}
        r = self.__send_request_to_daemon(requests.put,
                                          f"{self.daemon_url}/{self.simid}/"
                                          f"{task.get_workflow().get_name()}/tasks/"
                                          f"{task.get_name()}/addOutputFile", json_data=data)

        response = r.json()
        if not response["wrench_api_request_success"]:
            raise WRENCHException(response["failure_cause"])

    def _get_task_input_files(self, task: Task) -> List[File]:
        """
        Get a list of input files for a given task

        :param task: The task
        :type task: Task

        :return: The list of input files
        :rtype: List[File]

        :raises WRENCHException: if there is any error in the response
        """
        r = self.__send_request_to_daemon(requests.get, f"{self.daemon_url}/{self.simid}/"
                                                        f"{task.get_workflow().get_name()}/tasks/"
                                                        f"{task.get_name()}/inputFiles", json_data={})

        response = r.json()
        if response["wrench_api_request_success"]:
            file_list = []
            for filename in response["files"]:
                file_list.append(self.files[filename])
            return file_list
        raise WRENCHException(response["failure_cause"])

    def _get_task_output_files(self, task: Task) -> List[File]:
        """
        Get a list of output files for a given task

        :param task: the task
        :type task: Task

        :return: The list of output files
        :rtype: List[File]

        :raises WRENCHException: if there is any error in the response
        """
        r = self.__send_request_to_daemon(requests.get, f"{self.daemon_url}/{self.simid}/"
                                                        f"{task.get_workflow().get_name()}/tasks/"
                                                        f"{task.get_name()}/outputFiles", json_data={})

        response = r.json()
        if response["wrench_api_request_success"]:
            file_list = []
            for filename in response["files"]:
                file_list.append(self.files[filename])
            return file_list
        raise WRENCHException(response["failure_cause"])

    def _file_get_size(self, file: File) -> int:
        """
        Get the number of bytes for a given file
        :param file: the file
        :type file: File

        :return: The size of the file in bytes
        :rtype: int

        :raises WRENCHException: if there is any error in the response
        """
        r = self.__send_request_to_daemon(requests.get, f"{self.daemon_url}/{self.simid}"
                                                        f"/files/{file.get_name()}/size", json_data={})

        response = r.json()
        if response["wrench_api_request_success"]:
            return response["size"]
        raise WRENCHException(response["failure_cause"])

    def _task_get_flops(self, task: Task) -> float:
        """
        Get the number of flops in a task
        :param task: the task
        :type task: Task

        :return: a number of flops
        :rtype: float

        :raises WRENCHException: if there is any error in the response
        """
        r = self.__send_request_to_daemon(requests.get,
                                          f"{self.daemon_url}/{self.simid}/"
                                          f"{task.get_workflow().get_name()}/tasks/"
                                          f"{task.get_name()}/taskGetFlops",
                                          json_data={})

        response = r.json()
        if response["wrench_api_request_success"]:
            return response["flops"]
        raise WRENCHException(response["failure_cause"])

    def _task_get_min_num_cores(self, task: Task) -> int:
        """
        Get the task's minimum number of required cores
        :param task: the task
        :type task: Task

        :return: a number of cores
        :rtype: int

        :raises WRENCHException: if there is any error in the response
        """
        data = {}
        r = self.__send_request_to_daemon(requests.get,
                                          f"{self.daemon_url}/{self.simid}/"
                                          f"{task.get_workflow().get_name()}/tasks/"
                                          f"{task.get_name()}/taskGetMinNumCores",
                                          json_data=data)

        response = r.json()
        if response["wrench_api_request_success"]:
            return response["min_num_cores"]
        raise WRENCHException(response["failure_cause"])

    def _task_get_max_num_cores(self, task: Task) -> int:
        """
        Get the task's maximum number of required cores
        :param task: the task
        :type task: Task

        :return: a number of cores
        :rtype: int

        :raises WRENCHException: if there is any error in the response
        """
        data = {}
        r = self.__send_request_to_daemon(requests.get,
                                          f"{self.daemon_url}/{self.simid}/"
                                          f"{task.get_workflow().get_name()}/tasks/"
                                          f"{task.get_name()}/taskGetMaxNumCores",
                                          json_data=data)

        response = r.json()
        if response["wrench_api_request_success"]:
            return response["max_num_cores"]
        raise WRENCHException(response["failure_cause"])

    def _task_get_memory(self, task: Task) -> float:
        """
        Get the task's memory requirement
        :param task: the task
        :type task: Task

        :return: a memory footprint in bytes
        :rtype: float

        :raises WRENCHException: if there is any error in the response
        """
        data = {}
        r = self.__send_request_to_daemon(requests.get,
                                          f"{self.daemon_url}/{self.simid}/"
                                          f"{task.get_workflow().get_name()}/tasks/"
                                          f"{task.get_name()}/taskGetMemory", json_data=data)

        response = r.json()
        if response["wrench_api_request_success"]:
            return response["memory"]
        raise WRENCHException(response["failure_cause"])

    def _task_get_start_date(self, task: Task) -> float:
        """
        Get the task's start date
        :param task: the task
        :type task: Task

        :return: a date in seconds
        :rtype: float

        :raises WRENCHException: if there is any error in the response
        """
        r = self.__send_request_to_daemon(requests.get,
                                          f"{self.daemon_url}/{self.simid}/"
                                          f"{task.get_workflow().get_name()}/tasks/{task.get_name()}/"
                                          f"taskGetStartDate", json_data={})

        response = r.json()
        if response["wrench_api_request_success"]:
            return response["time"]
        raise WRENCHException(response["failure_cause"])

    def _task_get_end_date(self, task: Task) -> float:
        """
        Get the task's end date
        :param task: the task
        :type task: Task

        :return: a date in seconds
        :rtype: float

        :raises WRENCHException: if there is any error in the response
        """
        r = self.__send_request_to_daemon(requests.get,
                                          f"{self.daemon_url}/{self.simid}/"
                                          f"{task.get_workflow().get_name()}/tasks/{task.get_name()}/"
                                          f"taskGetEndDate", json_data={})

        response = r.json()
        if response["wrench_api_request_success"]:
            return response["time"]
        raise WRENCHException(response["failure_cause"])

    def _add_compute_action(self, compound_job: CompoundJob, name: str, flops: float, ram: float,
                           max_num_cores: int, min_num_cores: int, parallel_model: tuple) -> Action:
        """
        Add a compute action

        :param compound_job: compound job object this action is a part of
        :type compound_job: CompoundJob
        :param name: name of compute action
        :type name: str
        :param flops: number of flops this action has
        :type flops: float
        :param ram: amount of ram this action has
        :type ram: float
        :param max_num_cores: maximum number of cores this action can have
        :type max_num_cores: long
        :param min_num_cores: minimum number of cores this action can have
        :type min_num_cores: long
        :param parallel_model: type of parallel model and settings for it
        :type parallel_model: tuple

        :return: the action name
        :rtype: Action

        :raises WRENCHException: if there is any error in the response
        """
        data = {"name": name, "flops": flops, "ram": ram,
                "min_num_cores": min_num_cores,  "max_num_cores": max_num_cores, "parallel_model": parallel_model}

        r = self.__send_request_to_daemon(requests.post, f"{self.daemon_url}/{self.simid}/compoundJobs/"
                                                         f"{compound_job.get_name()}/addComputeAction", json_data=data)

        response = r.json()

        if response["wrench_api_request_success"]:
            compute_action = ComputeAction(self, compound_job, response["name"], flops, ram,
                                           min_num_cores, max_num_cores, parallel_model)
            compound_job.actions.append(compute_action)
            return compute_action
        raise WRENCHException(response["failure_cause"])

    def _add_file_copy_action(self, compound_job: CompoundJob, name: str, file: File,
                             src_storage_service: StorageService, dest_storage_service: StorageService) -> Action:
        """
        Add a file copy action

        :param self: simulation object
        :type self: simulation
        :param compound_job: compound job object
        :type compound_job: CompoundJob
        :param name: name of file copy action
        :type name: str
        :param file: name of file being copied
        :type file: File
        :param src_storage_service: source storage service being copied from
        :type src_storage_service: StorageService
        :param dest_storage_service: destination storage service being copied to
        :type dest_storage_service: StorageService

        :return: the action name
        :rtype: Action

        :raises WRENCHException: if there is any error in the response
        """
        data = {"name": name, "file_name": file.get_name(), "src_storage_service_name": src_storage_service.get_name(),
                "dest_storage_service_name": dest_storage_service.get_name()}
        r = self.__send_request_to_daemon(requests.post, f"{self.daemon_url}/{self.simid}/compoundJobs/"
                                                         f"{compound_job.get_name()}/addFileCopyAction", json_data=data)

        response = r.json()

        if response["wrench_api_request_success"]:
            if response["uses_scratch"] == "1":
                uses_scratch = True
            else:
                uses_scratch = False

            file_copy_action = FileCopyAction(self, compound_job, response["name"], file, src_storage_service,
                                              dest_storage_service, uses_scratch)
            compound_job.actions.append(file_copy_action)
            return file_copy_action
        raise WRENCHException(response["failure_cause"])

    def _add_file_delete_action(self, compound_job: CompoundJob, name: str, file: File,
                               storage_service: StorageService) -> Action:
        """
        Add a file delete action

        :param self: simulation object
        :type self: simulation
        :param compound_job: compound job object
        :type compound_job: CompoundJob
        :param name: name of file delete action
        :type name: str
        :param file: name of file being deleted
        :type file: File
        :param storage_service: storage service file is deleted from
        :type storage_service: StorageService

        :return: the action name
        :rtype: Action

        :raises WRENCHException: if there is any error in the response
        """
        data = {"name": name, "file_name": file.get_name(), "storage_service_name": storage_service.get_name()}
        r = self.__send_request_to_daemon(requests.post, f"{self.daemon_url}/{self.simid}/compoundJobs/"
                                                         f"{compound_job.get_name()}/addFileDeleteAction",
                                                         json_data=data)

        response = r.json()

        if response["wrench_api_request_success"]:
            if response["uses_scratch"] == "1":
                uses_scratch = True
            else:
                uses_scratch = False

            file_delete_action = FileDeleteAction(self, compound_job, response["name"], file, storage_service,
                                                  uses_scratch)
            compound_job.actions.append(file_delete_action)
            return file_delete_action
        raise WRENCHException(response["failure_cause"])

    def _add_file_write_action(self, compound_job: CompoundJob, name: str, file: File,
                              storage_service: StorageService) -> Action:
        """
        Add a file write action

        :param self: simulation object
        :type self: simulation
        :param compound_job: compound job object
        :type compound_job: CompoundJob
        :param name: name of file write action
        :type name: str
        :param file: name of file to write
        :type file: File
        :param storage_service: storage service to write the file to
        :type storage_service: StorageService

        :return: the action name
        :rtype: Action

        :raises WRENCHException: if there is any error in the response
        """
        data = {"name": name, "file_name": file.get_name(), "storage_service_name": storage_service.get_name()}
        r = self.__send_request_to_daemon(requests.post, f"{self.daemon_url}/{self.simid}/compoundJobs/"
                                                         f"{compound_job.get_name()}/addFileWriteAction",
                                                         json_data=data)

        response = r.json()

        if response["wrench_api_request_success"]:
            if response["uses_scratch"] == "1":
                uses_scratch = True
            else:
                uses_scratch = False

            file_write_action = FileWriteAction(self, compound_job, response["name"], file, storage_service,
                                                uses_scratch)
            compound_job.actions.append(file_write_action)
            return file_write_action
        raise WRENCHException(response["failure_cause"])

    def _add_file_read_action(self, compound_job: CompoundJob, name: str, file: File, storage_service: StorageService,
                             num_bytes_to_read: float) -> Action:
        """
        Add a file read action
        :param compound_job: the action's compound job
        :type compound_job: str
        :param name: name of the action
        :type name: str
        :param file: the file to read
        :type file: File
        :param storage_service: the storage service the file is stored in
        :type storage_service: StorageService
        :param num_bytes_to_read: the number of bytes to read from the file
        :type num_bytes_to_read: float
        :return: the action name
        :rtype: Action

        :raises WRENCHException: if there is any error in the response
        """
        data = {"name": name, "file_name": file.get_name(), "storage_service_name": storage_service.get_name(),
                "num_bytes_to_read": num_bytes_to_read}
        r = self.__send_request_to_daemon(requests.post, f"{self.daemon_url}/{self.simid}/compoundJobs/"
                                                         f"{compound_job.get_name()}/addFileReadAction",
                                                         json_data=data)

        response = r.json()

        if response["wrench_api_request_success"]:
            if response["uses_scratch"] == "1":
                uses_scratch = True
            else:
                uses_scratch = False

            file_read_action = FileReadAction(self, compound_job, response["name"], file, storage_service,
                                                response["num_bytes_to_read"], uses_scratch)
            compound_job.actions.append(file_read_action)
            return file_read_action
        raise WRENCHException(response["failure_cause"])

    def _add_sleep_action(self, compound_job: CompoundJob, name: str, sleep_time: float) -> Action:
        """
        Add a sleep action

        :param compound_job: compound job object this action is a part of
        :type compound_job: CompoundJob
        :param name: name of sleep action
        :type name: str
        :param sleep_time: time to sleep
        :type sleep_time: float

        :return: the action name
        :rtype: Action

        :raises WRENCHException: if there is any error in the response
        """
        data = {"name": name, "sleep_time": sleep_time}
        r = self.__send_request_to_daemon(requests.post, f"{self.daemon_url}/{self.simid}/compoundJobs/"
                                                         f"{compound_job.get_name()}/addSleepAction", json_data=data)

        response = r.json()

        if response["wrench_api_request_success"]:
            sleep_action = SleepAction(self, compound_job, response["sleep_action_name"], sleep_time)
            compound_job.actions.append(sleep_action)
            return sleep_action
        raise WRENCHException(response["failure_cause"])

    def _add_parent_job(self, compound_job: CompoundJob, parent_compound_job: CompoundJob) -> None:
        """
        Add a parent compound job to this compound job

        :param compound_job: compound job object
        :type compound_job: CompoundJob
        :param parent_compound_job: parent compound job
        :type compound_job: CompoundJob

        :return:

        :raises WRENCHException: if there is any error in the response
        """

        data = {"parent_compound_job": parent_compound_job.get_name()}
        r = self.__send_request_to_daemon(requests.post,
                                          f"{self.daemon_url}/{self.simid}/{compound_job.get_name()}/addParentJob",
                                          json_data=data)
        print(r)
        response = r.json()


        if response["wrench_api_request_success"]:
            return
        raise WRENCHException(response["failure_cause"])

    def _create_vm(self,
                   service: CloudComputeService,
                   num_cores: int,
                   ram_memory: float,
                   property_list: dict[str, str],
                   message_payload_list: dict[str, float]) -> VirtualMachine:
        """
        Create a VM instance
        :param service: the cloud compute service
        :type service: CloudComputeService
        :param num_cores: the number of cores for the VM
        :type num_cores: int
        :param ram_memory: the VM’s RAM memory_manager_service capacity
        :type ram_memory: float
        :param property_list: a property list for the CloudComputeService that will run on the VM
               ({} means “use all defaults”)
        :type property_list: dict
        :param message_payload_list: a message payload list for the CloudComputeService that will run on the VM
               ({} means “use all defaults”)
        :type message_payload_list: dict
        :return: A virtual machine object
        :rtype: VirtualMachine

        :raises WRENCHException: if there is any error in the response
        """

        data = {"service_name": service.get_name(), "num_cores": num_cores, "ram_memory": ram_memory,
                "property_list": json.dumps(property_list),
                "message_payload_list": json.dumps(message_payload_list)}

        r = self.__send_request_to_daemon(requests.post, f"{self.daemon_url}/{self.simid}/"
                                                         f"createVM", json_data=data)
        response = r.json()

        if response["wrench_api_request_success"]:
            return VirtualMachine(self, service, response["vm_name"])
        raise WRENCHException(response["failure_cause"])

    def _start_vm(self, vm: VirtualMachine) -> BareMetalComputeService:
        """
        Starts a VM the bare metal compute service associated to a vm
        :param vm: the VM
        :type vm: VirtualMachine
        :return: A bare metal compute service
        :rtype: BareMetalComputeService
        """
        data = {"service_name": vm.get_cloud_compute_service().get_name(), "vm_name": vm.get_name()}

        r = self.__send_request_to_daemon(requests.post, f"{self.daemon_url}/{self.simid}/"
                                                         f"startVM", json_data=data)
        response = r.json()

        if response["wrench_api_request_success"]:
            mbcs_name = response["service_name"]
            self.compute_services[mbcs_name] = BareMetalComputeService(self, mbcs_name)
            return self.compute_services[mbcs_name]
        raise WRENCHException(response["failure_cause"])

    def _shutdown_vm(self, vm: VirtualMachine):
        """
        Shutdowns a VM
        :param vm: the VM
        :type vm: VirtualMachine
        """

        data = {"service_name": vm.get_cloud_compute_service().get_name(), "vm_name": vm.get_name()}

        r = self.__send_request_to_daemon(requests.post, f"{self.daemon_url}/{self.simid}/"
                                                         f"shutdownVM", json_data=data)
        response = r.json()

        if response["wrench_api_request_success"]:
            return
        raise WRENCHException(response["failure_cause"])

    def _destroy_vm(self, vm: VirtualMachine):
        """
        Destroy a VM
        :param vm: the VM
        :type vm: VirtualMachine
        """

        data = {"service_name": vm.get_cloud_compute_service().get_name(), "vm_name": vm.get_name()}

        r = self.__send_request_to_daemon(requests.post, f"{self.daemon_url}/{self.simid}/"
                                                         f"destroyVM", json_data=data)
        response = r.json()

        if response["wrench_api_request_success"]:
            return
        raise WRENCHException(response["failure_cause"])

    def _is_vm_running(self, vm: VirtualMachine) -> bool:
        """
        Returns true if the VM is running
        :param vm: the VM
        :type vm: VirtualMachine
        :return: True or False
        :rtype: bool
        """
        data = {"compute_service_name": vm.get_cloud_compute_service().get_name(), "vm_name": vm.get_name()}
        r = self.__send_request_to_daemon(requests.get, f"{self.daemon_url}/{self.simid}/"
                                                        f"isVMRunning", json_data=data)
        response = r.json()

        if response["wrench_api_request_success"]:
            return response["result"]
        raise WRENCHException(response["failure_cause"])

    def _is_vm_down(self, vm: VirtualMachine) -> bool:
        """
        Returns true if the VM is down
        :param vm: the VM
        :type vm: VirtualMachine
        :return: True or False
        :rtype: bool
        """
        data = {"compute_service_name": vm.get_cloud_compute_service().get_name(), "vm_name": vm.get_name()}
        r = self.__send_request_to_daemon(requests.get, f"{self.daemon_url}/{self.simid}/"
                                                        f"isVMDown", json_data=data)
        response = r.json()

        if response["wrench_api_request_success"]:
            return response["result"]
        raise WRENCHException(response["failure_cause"])

    def _suspend_vm(self, vm: VirtualMachine):
        """
        Suspend a VM
        :param vm: the VM
        :type vm: VirtualMachine
        """
        data = {"compute_service_name": vm.get_cloud_compute_service().get_name(), "vm_name": vm.get_name()}
        r = self.__send_request_to_daemon(requests.post, f"{self.daemon_url}/{self.simid}/"
                                                         f"suspendVM", json_data=data)
        response = r.json()

        if response["wrench_api_request_success"]:
            return
        raise WRENCHException(response["failure_cause"])

    def _is_vm_suspended(self, vm: VirtualMachine) -> bool:
        """
        Returns true if the VM is suspended
        :param vm: the VM
        :type vm: VirtualMachine
        :return: True or False
        :rtype: bool
        """
        data = {"compute_service_name": vm.get_cloud_compute_service().get_name(), "vm_name": vm.get_name()}
        r = self.__send_request_to_daemon(requests.get, f"{self.daemon_url}/{self.simid}/"
                                                        f"isVMSuspended", json_data=data)
        response = r.json()

        if response["wrench_api_request_success"]:
            return response["result"]
        raise WRENCHException(response["failure_cause"])

    def _resume_vm(self, vm: VirtualMachine):
        """
        Resume a suspended VM
        :param vm: the VM
        :type vm: VirtualMachine
        """
        data = {"compute_service_name": vm.get_cloud_compute_service().get_name(), "vm_name": vm.get_name()}
        r = self.__send_request_to_daemon(requests.post, f"{self.daemon_url}/{self.simid}/"
                                                         f"resumeVM", json_data=data)
        response = r.json()

        if response["wrench_api_request_success"]:
            return
        raise WRENCHException(response["failure_cause"])

    def _supports_compound_jobs(self, cs: ComputeService) -> bool:
        """
        Returns true if the compute service supports compound jobs
        :param cs: the compute service
        :type cs: ComputeService
        :return: True or False
        :rtype: bool
        """
        data = {"compute_service_name": cs.get_name()}
        r = self.__send_request_to_daemon(requests.get, f"{self.daemon_url}/{self.simid}/"
                                                        f"supportsCompoundJobs", json_data=data)
        response = r.json()
        return response["result"]

    def _supports_pilot_jobs(self, cs: ComputeService) -> bool:
        """
        Returns true if the compute service supports pilot jobs
        :param cs: the compute service
        :type cs: ComputeService
        :return: True or False
        :rtype: bool
        """
        data = {"compute_service_name": cs.get_name()}
        r = self.__send_request_to_daemon(requests.get, f"{self.daemon_url}/{self.simid}/"
                                                        f"supportsPilotJobs", json_data=data)
        response = r.json()
        return response["result"]

    def _supports_standard_jobs(self, cs: ComputeService) -> bool:
        """
        Returns true if the compute service supports standard jobs
        :param cs: the compute service
        :type cs: ComputeService
        :return: True or False
        :rtype: bool
        """
        data = {"compute_service_name": cs.get_name()}
        r = self.__send_request_to_daemon(requests.get, f"{self.daemon_url}/{self.simid}/"
                                                        f"supportsStandardJobs", json_data=data)
        response = r.json()
        return response["result"]

    def _workflow_create_task(self, workflow: Workflow, name: str, flops: float, min_num_cores: int, max_num_cores: int,
                              memory: float) -> Task:
        """
        Add a task to the workflow
        :param workflow: the workflow
        :type workflow: Workflow
        :param name: task name
        :type name: str
        :param flops: number of flops
        :type flops: float
        :param min_num_cores: minimum number of cores
        :type min_num_cores: int
        :param max_num_cores: maximum number of cores
        :type max_num_cores: int
        :param memory: memory requirement in bytes
        :type memory: float

        :return: A task object
        :rtype: Task

        :raises WRENCHException: if there is any error in the response
        """
        data = {"workflow_name": workflow.get_name(),
                "name": name,
                "flops": flops,
                "min_num_cores": min_num_cores,
                "max_num_cores": max_num_cores,
                "memory": memory}
        r = self.__send_request_to_daemon(requests.put, f"{self.daemon_url}/{self.simid}/"
                                                        f"{workflow.name}/createTask", json_data=data)

        response = r.json()
        if response["wrench_api_request_success"]:
            workflow.tasks[name] = Task(self, workflow, name)
            return workflow.tasks[name]
        raise WRENCHException(response["failure_cause"])

    def _workflow_get_input_files(self, workflow: Workflow) -> List[File]:
        """
        Get a list of all input files of the workflow
        :param workflow: the workflow
        :type workflow: Workflow
        :return: The list of input files
        :rtype: List[File]

        :raises WRENCHException: if there is any error in the response
        """
        r = self.__send_request_to_daemon(requests.post, f"{self.daemon_url}/{self.simid}/"
                                                         f"{workflow.get_name()}/getInputFiles", json_data={})

        response = r.json()
        if response["wrench_api_request_success"]:
            file_list = []
            for filename in response["files"]:
                file_list.append(self.files[filename])
            return file_list
        raise WRENCHException(response["failure_cause"])

    def _add_entry_to_file_registry_service(self, file_registry_service: FileRegistryService, file: File, storage_service: StorageService):
        """
        Add an entry (file/storage service) to a file registry service
        :param file_registry_service: the file registry service
        :type file_registry_service: FileRegistryService
        :param file: the file
        :type file: File
        :param storage_service: the storage service
        :type storage_service: StorageService

        :raises WRENCHException: if there is any error in the response
        """
        data = {"file_name": file.get_name(),
                "storage_service_name": storage_service.get_name(),}
        r = self.__send_request_to_daemon(requests.post, f"{self.daemon_url}/{self.simid}/fileRegistryServices/"
                                                         f"{file_registry_service.get_name()}/addEntry", json_data=data)

        response = r.json()
        if not response["wrench_api_request_success"]:
            raise WRENCHException(response["failure_cause"])
        return

    def _lookup_entry_in_file_registry_service(self, file_registry_service: FileRegistryService, file: File) -> List[StorageService]:
        """
        Blah
        :param file_registry_service:
        :param file:
        :return List of storage services associated with file:
        :rtype: StorageService[]
        """
        data = {"file_name": file.get_name()}

        r = self.__send_request_to_daemon(requests.post, f"{self.daemon_url}/{self.simid}/fileRegistryServices/"
                                                         f"{file_registry_service.get_name()}/lookupEntry",
                                          json_data=data)

        response = r.json()
        if response["wrench_api_request_success"]:
            ss_list = []
            for storage_service_name in response["storage_services"]:
                ss_list.append(self.storage_services[storage_service_name])
            return ss_list
        raise WRENCHException(response["failure_cause"])

    def _remove_entry_from_file_registry_service(self, file_registry_service: FileRegistryService, file: File, storage_service: StorageService):
        """
        Remove an entry (file/storage service) from a file registry service
        :param file_registry_service: the file registry service
        :type file_registry_service: FileRegistryService
        :param file: the file
        :type file: File
        :param storage_service: the storage service
        :type storage_service: StorageService

        :raises WRENCHException: if there is any error in the response
        """
        data = {"file_name": file.get_name(),
                "storage_service_name": storage_service.get_name(),}
        r = self.__send_request_to_daemon(requests.post, f"{self.daemon_url}/{self.simid}/fileRegistryServices/"
                                                         f"{file_registry_service.get_name()}/removeEntry", json_data=data)

        response = r.json()
        if not response["wrench_api_request_success"]:
            raise WRENCHException(response["failure_cause"])
        return

    ###############################
    # Private methods
    ###############################

    def __json_event_to_dict(self, json_event: Dict[str, str]) -> Dict[str, Union[str, StandardJob, ComputeService]]:
        """
        :param json_event:
        :type json_event: Dict[str, str]

        :return
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
            event_dict["standard_job"] = self.standard_jobs[json_event["job_name"]]
            return event_dict
        elif json_event["event_type"] == "job_failure":
            event_dict["event_type"] = json_event["event_type"]
            event_dict["compute_service"] = self.compute_services[json_event["compute_service_name"]]
            event_dict["submit_date"] = json_event["submit_date"]
            event_dict["end_date"] = json_event["end_date"]
            event_dict["event_date"] = json_event["event_date"]
            event_dict["standard_job"] = self.standard_jobs[json_event["job_name"]]
            event_dict["failure_cause"] = json_event["failure_cause"]
            return event_dict

        raise WRENCHException("Unknown event type " + json_event["event_type"])
