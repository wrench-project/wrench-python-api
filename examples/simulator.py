#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 The WRENCH Team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

import pathlib
import os
import sys

import wrench

if __name__ == "__main__":

    if len(sys.argv) != 2:
        sys.stderr.write(f"Usage: {sys.argv[0]} <# seconds of real time to sleep during simulation>\n")
        exit(1)

    try:
        current_dir = pathlib.Path(__file__).parent.resolve()
        platform_file_path = pathlib.Path(current_dir / "three_host_platform.xml")
        
        simulation = wrench.Simulation()
        simulation.start(platform_file_path, "ControllerHost")

        print(f"New simulation, time is {simulation.get_simulated_time()}")

        hosts = simulation.get_all_hostnames()
        print(f"Hosts in the platform are: {hosts}")

        print(f"Creating compute resources")
        cr_name = ["cr1", "cr2", "cr3"]
        cr_cores = (6, 4, 8)
        cr_memory = (16.0, 24.0, 32.0)
        print("Creating a bare-metal compute service on ComputeHost...")
        cs = simulation.create_bare_metal_compute_service("ComputeHost", (cr_name, (cr_cores, cr_memory)))

        print(f"Created compute service has name {cs.get_name()}")

        print("Creating a simple storage service on StorageHost...")
        ss = simulation.create_simple_storage_service("StorageHost")
        print(f"Created storage service has name {ss.get_name()}")

        print("Creating a file registry service on ControllerHost...")
        frs = simulation.create_file_registry_service("ControllerHost")
        print(f"Created file registry service has name {frs.get_name()}")

        print("Adding a 1kB file to the workflow...")
        file1 = simulation.add_file("file1", 1024)
        print(f"Created file {file1}")

        print("Create a copy of the file on the storage service")
        ss.create_file_copy(file1)

        print("Sleeping for 10 seconds...")
        simulation.sleep(10)
        print(f"Time now is {simulation.get_simulated_time()}")

        print("Creating a task")
        task1 = simulation.create_task("task1", 100.0, 1, 1, 0)
        print(f"Just created a task with flops={task1.get_flops()}" +
              f", min_num_cores={task1.get_min_num_cores()}" +
              f", max_num_cores={task1.get_max_num_cores()}" +
              f", memory={task1.get_memory()}")

        # task1.add_input_file(file1)
        # print(f"Attached file {file1} as input file to task {task1.get_name()}")

        # print(f"All input files of the workflow: {simulation.get_input_files()}")
        # print(f"Input files of the task {task1.get_name()}: {task1.get_input_files()}")
        # simulation.stage_files(ss)
        # print(f"Input files staged on storage {ss}")

        print("Creating a standard job with a single 100.0 flop task")
        job = simulation.create_standard_job([task1])

        print(f"Created standard job has name {job.get_name()}")

        print("Submitting the standard job to the compute service...")
        cs.submit_standard_job(job)
        print("Job submitted!")

        print("Sleeping for 1000 seconds...")
        simulation.sleep(1000)

        print(f"Time now is {simulation.get_simulated_time()}")

        print("Getting simulation events that have occurred while I slept...")
        events = simulation.get_simulation_events()
        for event in events:
            print(f"  - Event: {event}")

        print(f"Sleeping {sys.argv[1]} seconds in real time")
        os.system(f"sleep {sys.argv[1]}")

        print("Creating another task")
        task2 = simulation.create_task("task2", 100.0, 1, 1, 0)

        print("Creating another job...")
        other_job = simulation.create_standard_job([task2])
        print(f"Created standard job has name {other_job.get_name()}")

        print("Submitting the standard job to the compute service...")
        cs.submit_standard_job(other_job)
        print("Job submitted!")

        print("Synchronously waiting for the next simulation event...")
        event = simulation.wait_for_next_event()
        print(f"  - Event: {event}")

        print("That Job's tasks are:")
        tasks = event["job"].get_tasks()
        for t in tasks:
            print(f"  - {t.get_name()}")

        print(f"Time is {simulation.get_simulated_time()}")

        print("Terminating simulation daemon")
        simulation.terminate()

    except wrench.WRENCHException as e:
        print(f"Error: {e}")
        exit(1)
