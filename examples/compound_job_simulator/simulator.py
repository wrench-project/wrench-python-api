#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 The WRENCH Team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.


import pathlib
import wrench

if __name__ == "__main__":

    try:
        # Instantiating the simulation based on a platform description file
        current_dir = pathlib.Path(__file__).parent.resolve()
        platform_file_path = pathlib.Path(current_dir / "sample_platform.xml")

        # Creating a new WRENCH simulation
        simulation = wrench.Simulation()

        # Starting the simulation, with this simulated process running on the host ControllerHost
        with open(platform_file_path, "r") as platform_file:
            xml_string = platform_file.read()
        simulation.start(xml_string, "ControllerHost")

        hosts = simulation.get_all_hostnames()
        print(f"Hosts in the platform are: {hosts}")

        # Creating a couple of compute services
        print(f"Creating compute services")
        print("Creating a bare-metal compute service on ComputeHost...")
        bmcs = simulation.create_bare_metal_compute_service(
            "BatchHeadHost",
            {"BatchHost1": (6, 10.0),
             "BatchHost2": (6, 12.0)},
            "/scratch",
            {"BareMetalComputeServiceProperty::THREAD_STARTUP_OVERHEAD": "12s"},
            {"ServiceMessagePayload::STOP_DAEMON_MESSAGE_PAYLOAD": 1024.0})

        print(f"Creating a cloud compute service")
        ccs = simulation.create_cloud_compute_service("CloudHeadHost",
                                                      ["CloudHost1", "CloudHost2"],
                                                      "/scratch",
                                                      {"CloudComputeServiceProperty::VM_BOOT_OVERHEAD": "5s"},
                                                      {"ServiceMessagePayload::STOP_DAEMON_MESSAGE_PAYLOAD": 1024.0})

        # Creating a file registry service
        print("Creating a file registry service on ControllerHost...")
        frs = simulation.create_file_registry_service("ControllerHost")
        print(f"Created file registry service has name {frs.get_name()}")

        # Creating storage services
        print("Creating a simple storage service on StorageHost...")
        ss1 = simulation.create_simple_storage_service("StorageHost", ["/"])
        print(f"Created storage service has name {ss1.get_name()}")
        print("Creating another simple storage service on ControllerHost...")
        ss2 = simulation.create_simple_storage_service("ControllerHost", ["/"])
        print(f"Created storage service has name {ss2.get_name()}")

        # Creating files
        print("Adding a 1kB file to the simulation...")
        file1 = simulation.add_file("file1", 1024)
        print(f"Created file {file1}")
        print("Adding another 1kB file to the simulation...")
        file2 = simulation.add_file("file2", 1024)
        print(f"Created file {file2}")

        # Adding a file to a storage service
        print(f"Creating a copy of {file1} on the storage service")
        ss1.create_file_copy(file1)

        # Creating a compound job
        cj = simulation.create_compound_job("")
        print(f"Created compound job with name {cj.get_name()}")

        # Add a file write action to compound job
        fwa = cj.add_file_write_action("FileWriteAction1", file1, ss1)
        print(f"Adding {fwa.get_name()} to {cj.get_name()}")

        # Add a file read action to compound job
        fra = cj.add_file_read_action("FileReadAction1", file1, ss1)
        print(f"Adding {fra.get_name()} to {cj.get_name()}")

        # Add a file copy action to compound job
        fca = cj.add_file_copy_action("FileCopyAction1", file1, ss1, ss2)
        print(f"Adding {fca.get_name()} to {cj.get_name()}")

        # Add a file delete action to compound job
        fda = cj.add_file_delete_action("FileDeleteAction1", file1, ss1)
        print(f"Adding {fda.get_name()} to {cj.get_name()}")

        # Add a sleep action to compound job
        sa = cj.add_sleep_action("SleepAction1", 5.0)
        print(f"Adding {sa.get_name()} to {cj.get_name()}")

        # print(f"Sleep Action getSleepTime = {sa.get_sleep_time()}")

        # # Add a parent compound job to another compound job
        cj2_0 = simulation.create_compound_job("")
        print(f"Created compound job with name {cj2_0.get_name()}")
        cj2_0.add_sleep_action("SleepAction2", 2.0)

        cj2_1 = simulation.create_compound_job("")
        print(f"Created compound job with name {cj2_1.get_name()}")
        cj2_1.add_sleep_action("SleepAction3", 2.0)

        print("Adding parent compound job")
        cj2_1.add_parent_job(cj2_0)

        print(f"Time before submitting compound jobs 2/3 is {simulation.get_simulated_time()}")

        print("Submitting the parent compound job to the base metal compute service...")
        bmcs.submit_compound_job(cj2_0)

        print(f"Time after submitting compound jobs 2/3 is {simulation.get_simulated_time()}")

        # Get the actions of compound job
        print(f"Compound Job's get_actions = {cj.get_actions()}")

        print("Submitting the compound job to the base metal compute service...")
        bmcs.submit_compound_job(cj)

        print("Synchronously waiting for the next simulation event...")
        event = simulation.wait_for_next_event()
        print(f"\t- Event: {event}")
        print(f"Time is {simulation.get_simulated_time()}")

        print("Synchronously waiting for the next simulation event...")
        event = simulation.wait_for_next_event()
        print(f"\t- Event: {event}")
        print(f"Time is {simulation.get_simulated_time()}")

        print("Terminating simulation")
        simulation.terminate()

    except wrench.WRENCHException as e:
        print(f"Error: {e}")
        exit(1)
