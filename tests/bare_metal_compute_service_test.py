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
import time

import wrench

if __name__ == "__main__":

    try:
        current_dir = pathlib.Path(__file__).parent.resolve()
        platform_file_path = pathlib.Path(current_dir / "sample_platform.xml")

        simulation = wrench.Simulation()
        simulation.start(platform_file_path, "ControllerHost")

        print(f"New simulation, time is {simulation.get_simulated_time()}")
        hosts = simulation.get_all_hostnames()
        print(f"Hosts in the platform are: {hosts}")

        print("Creating a bare-metal compute service on BatchHeadHost...")

        cs = simulation.create_bare_metal_compute_service(
            "BatchHeadHost",
            {"BatchHost1": (6, 10.0),
             "BatchHost2": (6, 12.0)},
            "/scratch",
            {"BareMetalComputeServiceProperty::THREAD_STARTUP_OVERHEAD": "12s"},
            {"ServiceMessagePayload::STOP_DAEMON_MESSAGE_PAYLOAD": 1024.0})

        print(f"Created compute service has name {cs.get_name()}")

        print(f"Compute service supported jobs")
        print(f"Supports Compound Jobs: {cs.supports_compound_jobs()}\n"
              f"Supports Pilot Jobs: {cs.supports_pilot_jobs()}\n"
              f"Supports Standard Jobs: {cs.supports_standard_jobs()}")

        print("Creating a simple storage service on StorageHost...")
        ss = simulation.create_simple_storage_service("StorageHost", ["/"])
        print(f"Created storage service has name {ss.get_name()}")

        print("Creating a file registry service on StorageHost...")
        frs = simulation.create_file_registry_service("ControllerHost")
        print(f"Created file registry service has name {frs.get_name()}")

        print("Creating a 2-task chain workflow...")
        file1 = simulation.add_file("file1", 1024)
        file2 = simulation.add_file("file2", 1024)
        file3 = simulation.add_file("file3", 1024)
        ss.create_file_copy(file1)
        task1 = simulation.create_task("task1", 10000000000, 1, 1, 0)
        task1.add_input_file(file1)
        task1.add_output_file(file2)
        task2 = simulation.create_task("task2", 200000000000, 1, 1, 0)
        task2.add_input_file(file2)
        task2.add_output_file(file3)

        print("Creating a standard job with both tasks")
        job = simulation.create_standard_job([task1, task2], {file1: ss, file2: ss, file3: ss})

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

        print(f"Task1's start date was: {task1.get_start_date()}")
        print(f"Task1's end date was: {task1.get_end_date()}")
        print(f"Task2's start date was: {task2.get_start_date()}")
        print(f"Task2's end date was: {task2.get_end_date()}")

        print(f"Time is {simulation.get_simulated_time()}")

        print("Terminating simulation daemon")
        simulation.terminate()

    except wrench.WRENCHException as e:
        print(f"Error: {e}")
        exit(1)
