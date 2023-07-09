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

        print(f"Simulation, time is {simulation.get_simulated_time()}")
        hosts = simulation.get_all_hostnames()
        print(f"Hosts in the platform are: {hosts}")
        print(f"Creating compute resources")

        print("Creating a cloud compute service on CloudHeadHost...")

        ccs = simulation.create_cloud_compute_service("CloudHeadHost",
                                                      ["CloudHost1", "CloudHost2"],
                                                      "/scratch",
                                                      {"CloudComputeServiceProperty::VM_BOOT_OVERHEAD": "5s"},
                                                      {"ServiceMessagePayload::STOP_DAEMON_MESSAGE_PAYLOAD": 1024.0})
        print(f"Created cloud compute service has name {ccs.get_name()}")

        print(f"Compute service supported jobs")
        print(f"Supports Compound Jobs: {ccs.supports_compound_jobs()}\n"
              f"Supports Pilot Jobs: {ccs.supports_pilot_jobs()}\n"
              f"Supports Standard Jobs: {ccs.supports_standard_jobs()}")

        print("Creating VM..")
        vm_name = ccs.create_vm(1, 100.0,
                                  {"CloudComputeServiceProperty::VM_BOOT_OVERHEAD": "5s"},
                                  {"ServiceMessagePayload::STOP_DAEMON_MESSAGE_PAYLOAD": 1024.0})

        vm_cs = ccs.start_vm(vm_name)

        print(f"Created and started a VM named {vm_name} that runs a bare metal compute service named {vm_cs.get_name()}")

        print(f"Submitting a job do the VM's bare metal compute service")
        task1 = simulation.create_task("task1", 10000000000.0, 1, 1, 0)
        job = simulation.create_standard_job([task1])
        vm_cs.submit_standard_job(job)
        print(f"Simulation, time is {simulation.get_simulated_time()}")
        print(f"Waiting for job completion...")
        event = simulation.wait_for_next_event()
        print(f"Simulation, time is {simulation.get_simulated_time()}")
        print(f"Got this event: {event}")

        print(f"Shutting down the VM")
        ccs.shutdown_vm(vm_name)

        print(f"(Re)starting  the VM")
        vm_cs = ccs.start_vm(vm_name)

        print(f"Submitting another job do the VM's bare metal compute service")
        task2 = simulation.create_task("task2", 10000000000.0, 1, 1, 0)
        job = simulation.create_standard_job([task2])
        vm_cs.submit_standard_job(job)
        print(f"Simulation, time is {simulation.get_simulated_time()}")
        print(f"Waiting for job completion...")
        event = simulation.wait_for_next_event()
        print(f"Simulation, time is {simulation.get_simulated_time()}")
        print(f"Got this event: {event}")

        print(f"(Re)Shutting down the VM")
        ccs.shutdown_vm(vm_name)

        print(f"Destroying the VM")
        ccs.destroy_vm(vm_name)

        try:
            ccs.destroy_vm(vm_name)
        except wrench.WRENCHException as e:
            pass

        # ToDo: In wrench daemon, the route starts with /api, anything to change?
        print("Terminating simulation daemon")
        simulation.terminate()

    except wrench.WRENCHException as e:
        print(f"Error: {e}")
        exit(1)