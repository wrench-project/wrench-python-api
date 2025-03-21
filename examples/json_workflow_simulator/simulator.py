#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 The WRENCH Team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

import json
import pathlib
import wrench
from typing import List, Dict

from wrench.simulation import Simulation  # For type checking
from wrench.task import Task  # For type checking
from wrench.compute_service import ComputeService  # For type checking


def pick_task_to_schedule(tasks: List[Task]):
    """
    A method to select a particular task to schedule. Right now, just selects
    the task with the largest flop
    """
    # pick the task with the largest flop amount
    max_flop = tasks[0].get_flops()
    target_task = tasks[0]
    for task in tasks[1:]:
        if task.get_flops() > max_flop:
            max_flop = task.get_flops()
            target_task = task
    return target_task


def pick_target_cs(compute_resources: Dict[ComputeService, Dict[str, float]], desired_num_cores: int) -> ComputeService:
    """
    A method to select a compute service on which to schedule a task. Right now,
    just selects the compute service with the largest flop rate
    """
    # pick the one with the largest core speed
    max_core_speed = 0
    target_cs = None
    for cs in compute_resources:
        # If there are no idle cores, don't consider this resource
        if compute_resources[cs]["num_idle_cores"] < desired_num_cores:
            continue
        if compute_resources[cs]["core_speed"] > max_core_speed:
            max_core_speed = compute_resources[cs]["core_speed"]
            target_cs = cs
    return target_cs


def schedule_tasks(simulation: Simulation, tasks_to_schedule: List[Task],
                   compute_resources: Dict[ComputeService, Dict[str, float]], storage_service):
    """
    A method that schedules tasks, using list scheduling, if possible
    """

    while True:
        # If no tasks left to schedule, we're done
        if len(tasks_to_schedule) == 0:
            break

        # Pick one of the tasks for scheduling
        task_to_schedule = pick_task_to_schedule(tasks_to_schedule)
        if task_to_schedule is None:
            break

        # Pick one of the compute services on which to schedule the task,
        # using the minimum number of cores for the task
        target_cs = pick_target_cs(compute_resources, task_to_schedule.get_min_num_cores())

        # If we didn't find a compute service, we're done
        if target_cs is None:
            break

        # Remove the task from future consideration
        tasks_to_schedule.remove(task_to_schedule)

        print(f"Scheduling task {task_to_schedule.get_name()} on compute service {target_cs.get_name()}...")

        # Create the dictionary of file locations, which in this case
        # is always the one storage service
        input_files = task_to_schedule.get_input_files()
        output_files = task_to_schedule.get_output_files()
        locations = {}
        for f in input_files:
            locations[f] = storage_service
        for f in output_files:
            locations[f] = storage_service

        # Create a standard job for the task
        job = simulation.create_standard_job([task_to_schedule], locations)

        # Submit the standard job for execution
        target_cs.submit_standard_job(job)

        # Update the number of idle cores of the target compute service
        compute_resources[target_cs]["num_idle_cores"] -= 1

    return


def main():
    try:
        # Create a new WRENCH simulation
        print(f"Instantiating a simulation...")
        simulation = wrench.Simulation()

        # Starting the simulation, with this simulated process running on the host UserHost
        # (it is sort of week that the hostname needs to be specified first before
        #  we get a change to call, for instance, get_all_hostnames(), which would
        #  allow to pick a host at random).
        user_host = "UserHost"
        print(f"Starting the simulation using the XML platform file...")
        current_dir = pathlib.Path(__file__).parent.resolve()
        platform_file_path = pathlib.Path(current_dir / "one_host_and_several_clusters.xml")
        with open(platform_file_path, "r") as platform_file:
            xml_string = platform_file.read()
        simulation.start(xml_string, user_host)

        # Get the list of all hostnames in the platform
        print(f"Getting the list of all hostnames...")
        list_of_hostnames = simulation.get_all_hostnames()

        if "UserHost" not in list_of_hostnames:
            raise Exception("This simulator assumes that the XML platform files has a host with hostname UserHost that"
                            " has a disk mounted at '/'")
        list_of_hostnames.remove("UserHost")

        # Start a storage service on the user host
        print(f"Starting a storage service...")
        ss = simulation.create_simple_storage_service(user_host, ["/"])

        # Creating a bare-metal compute service on ALL other hosts
        print(f"Creating {len(list_of_hostnames)} compute services...")
        running_bmcss = []
        for host in list_of_hostnames:
            bmcs = simulation.create_bare_metal_compute_service(host, {host: (-1, -1)}, "", {}, {})
            running_bmcss.append(bmcs)

        # Create a data structure that keeps track of the compute resources, which
        # will be used for scheduling
        print(f"Creating a convenient data structure for scheduling...")
        compute_resources: dict[ComputeService, dict] = {}
        for bmcs in running_bmcss:
            # print(f"Getting core counts...")
            per_host_num_cores = bmcs.get_core_counts()
            num_cores = per_host_num_cores[list(per_host_num_cores.keys())[0]]
            # print(f"Getting core flop rates...")
            per_host_core_speed = bmcs.get_core_flop_rates()
            core_speed = per_host_core_speed[list(per_host_core_speed.keys())[0]]
            compute_resources[bmcs] = {"num_idle_cores": num_cores, "core_speed": core_speed}
        # print(compute_resources)

        # Import the workflow from JSON
        print(f"Importing the workflow from JSON...")
        workflow_file_path = pathlib.Path(current_dir / "sample_wfcommons_workflow.json")
        f = open(workflow_file_path)
        json_doc = json.load(f)
        workflow = simulation.create_workflow_from_json(json_doc,
                                                        reference_flop_rate="100Mf",
                                                        ignore_machine_specs=True,
                                                        redundant_dependencies=False,
                                                        ignore_cycle_creating_dependencies=False,
                                                        min_cores_per_task=1,
                                                        max_cores_per_task=1,
                                                        enforce_num_cores=True,
                                                        ignore_avg_cpu=True,
                                                        show_warnings=True)

        # Create all needed files on the storage service
        print(f"Create all file copies on the storage service...")
        files = workflow.get_input_files()
        for f in files:
            ss.create_file_copy(f)


        # We are now ready to schedule the workflow
        print(f"Starting my main loop!")
        while not workflow.is_done():
            # Perform some scheduling, perhaps
            schedule_tasks(simulation, workflow.get_ready_tasks(), compute_resources, ss)

            # Wait for next event
            event = simulation.wait_for_next_event()
            if event["event_type"] != "standard_job_completion":
                print(f"\t- Event: {event}")  # Should make sure it's a job completion
                raise wrench.WRENCHException("Received an unexpected event")
            else:
                completed_job = event["standard_job"]
                completed_task_name = completed_job.get_tasks()[0].get_name()
                print(f"Task {completed_task_name} has completed!")
                compute_resources[event["compute_service"]]["num_idle_cores"] += 1

        print(f"Workflow execution completed at time {simulation.get_simulated_time()}!")

    except wrench.WRENCHException as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
