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

        print(f"Simulation, time is {simulation.get_simulated_time()}")

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

        # Creating a storage service
        print("Creating a simple storage service on StorageHost...")
        ss = simulation.create_simple_storage_service("StorageHost", ["/"])
        print(f"Created storage service has name {ss.get_name()}")

        print("Creating a file registry service on ControllerHost...")
        frs = simulation.create_file_registry_service("ControllerHost")
        print(f"Created file registry service has name {frs.get_name()}")

        print("Adding a 1kB file to the simulation...")
        file1 = simulation.add_file("file1", 1024)
        print(f"Created file {file1}")
        print("Adding another 1kB file to the simulation...")
        file2 = simulation.add_file("file2", 1024)
        print(f"Created file {file2}")

        print(f"Creating a copy of {file1} on the storage service")
        ss.create_file_copy(file1)

        # Add an entry to the file registry service
        print(f"Adding an entry for {file1} on the file registry service {frs.get_name()}")
        frs.add_entry(ss, file1)

        # Looking the entry
        ss_list = frs.lookup_entry(file1)
        print(f"Entries for file: {ss_list}")

        # Remove an entry to the file registry service
        print(f"Removing an entry for {file1} on the file registry service {frs.get_name()}")
        frs.remove_entry(ss, file1)

        # Looking the entry again (which should fail)
        ss_list = frs.lookup_entry(file1)
        print(f"Entries for file: {ss_list}")

        print("Sleeping for 10 seconds...")
        simulation.sleep(10)
        print(f"Time now is {simulation.get_simulated_time()}")

        print("Creating a workflow")
        workflow = simulation.create_workflow()

        print("Creating a task")
        task1 = workflow.add_task("task1", 100.0, 1, 1, 0)
        print(f"Just created a task with flops={task1.get_flops()}" +
              f", min_num_cores={task1.get_min_num_cores()}" +
              f", max_num_cores={task1.get_max_num_cores()}" +
              f", memory={task1.get_memory()}")

        task1.add_input_file(file1)
        print(f"Attached file {file1} as input file to task {task1.get_name()}")
        print(f"The list of input files for task {task1.get_name()} is: {task1.get_input_files()}")
        task1.add_output_file(file2)
        print(f"Attached file {file2} as output file to task {task1.get_name()}")
        print(f"The list of output files for task {task1.get_name()} is: {task1.get_output_files()}")

        print("Creating a standard job with the task, so that input/output files will be on the storage service")
        job = simulation.create_standard_job([task1], {file1: ss, file2: ss})

        print("Submitting the standard job to the base metal compute service...")
        bmcs.submit_standard_job(job)

        print("Sleeping for 1000 seconds...")
        simulation.sleep(1000)

        print(f"Time now is {simulation.get_simulated_time()}")
        print("Getting simulation events that have occurred while I slept...")
        events = simulation.get_events()
        for event in events:
            print(f"\t- Event: {event}")

        print("Creating another task")
        task2 = workflow.add_task("task2", 100.0, 1, 1, 0)

        print("Creating another job...")
        other_job = simulation.create_standard_job([task2], {})

        print("Creating a VM on the cloud compute service...")
        my_vm = ccs.create_vm(1, 100,
                              {"CloudComputeServiceProperty::VM_BOOT_OVERHEAD": "5s"}, {})

        print("Starting the VM...")
        vm_cs = my_vm.start()

        print("Submitting the standard job to the compute service running on the VM...")
        vm_cs.submit_standard_job(other_job)

        print("Synchronously waiting for the next simulation event...")
        event = simulation.wait_for_next_event()
        print(f"\t- Event: {event}")

        print(f"Time is {simulation.get_simulated_time()}")

        # Compound job
        # cjob = simulation.create_compound_job()
        # my_sleep_action_1 = cjob.add_sleep_action(name="", sleep_time=10)
        # print(my_sleep_action_1.get_sleep_time())
        # my_sleep_action_2 = cjob.add_sleep_action(name="my_sleep_2", sleep_time=20)
        # cjob.add_action_dependency(my_sleep_action_1, my_sleep_action_2)
        # list_of_actions = cjob.get_actions()
        # mcss.submit_compound_job(cjob)
        # if (my_sleep_action_1.get_state() == Action.RUNNING):
        #     print("Action is still running!")
        # if (my_sleep_action_1.get_state_as_string() == "RUNNING"):
        #    print("Action is still running!")

        print("Terminating simulation")

        simulation.terminate()

    except wrench.WRENCHException as e:
        print(f"Error: {e}")
        exit(1)
