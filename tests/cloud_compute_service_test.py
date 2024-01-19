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

        print("Creating VM...")
        my_vm = ccs.create_vm(1, 100,
                              {"CloudComputeServiceProperty::VM_BOOT_OVERHEAD": "5s"},
                              {"ServiceMessagePayload::STOP_DAEMON_MESSAGE_PAYLOAD": 1024.0})

        # Checking that we cannot shut down a non-started VM
        try:
            my_vm.shutdown()
            raise wrench.WRENCHException("Should not be able to shutdown a non-started VM")
        except wrench.WRENCHException as e:
            pass

        vm_cs = my_vm.start()

        # Doing it again, checking that we get an exception
        try:
            my_vm.start()
            raise wrench.WRENCHException("Should not be able to start a VM twice")
        except wrench.WRENCHException as e:
            pass

        print(f"Created and started a VM named {my_vm.get_name()} that runs a bare metal "
              f"compute service named {vm_cs.get_name()}")

        if not my_vm.is_running():
            raise wrench.WRENCHException("VM should be running")
        if my_vm.is_down():
            raise wrench.WRENCHException("VM should not be down")
        if my_vm.is_suspended():
            raise wrench.WRENCHException("VM should not be suspended")

        print(f"Suspending VM {my_vm.get_name()}")
        my_vm.suspend()
        if not my_vm.is_suspended():
            raise wrench.WRENCHException("VM should be suspended")

        print(f"Resuming VM {my_vm.get_name()}")
        my_vm.resume()
        if not my_vm.is_running():
            raise wrench.WRENCHException("VM should be running")

        print(f"Submitting a job do the VM's bare metal compute service")
        workflow = simulation.create_workflow()
        print(f"Created {workflow.name}")
        task1 = workflow.add_task("task1", 10000000000.0, 1, 1, 0)
        job = simulation.create_standard_job([task1], {})
        vm_cs.submit_standard_job(job)
        print(f"Simulation, time is {simulation.get_simulated_time()}")
        print(f"Waiting for job completion...")
        event = simulation.wait_for_next_event()
        print(f"Simulation, time is {simulation.get_simulated_time()}")
        print(f"Got this event: {event}")

        print(f"Shutting down the VM")
        my_vm.shutdown()
        if not my_vm.is_down():
            raise wrench.WRENCHException("VM should be down")

        # Doing it again, checking that we get an exception
        try:
            my_vm.shutdown()
            raise wrench.WRENCHException("Should not be able to shutdown a VM twice")
        except wrench.WRENCHException as e:
            pass

        print(f"(Re)starting  the VM")
        vm_cs = my_vm.start()
        if not my_vm.is_running():
            raise wrench.WRENCHException("VM should be running")

        print(f"Submitting another job do the VM's bare metal compute service")
        task2 = workflow.add_task("task2", 10000000000.0, 1, 1, 0)
        job = simulation.create_standard_job([task2], {})
        vm_cs.submit_standard_job(job)
        print(f"Simulation, time is {simulation.get_simulated_time()}")
        print(f"Waiting for job completion...")
        event = simulation.wait_for_next_event()
        print(f"Simulation, time is {simulation.get_simulated_time()}")
        print(f"Got this event: {event}")

        print(f"(Re)Shutting down the VM")
        my_vm.shutdown()
        if not my_vm.is_down():
            raise wrench.WRENCHException("VM should be down")

        print(f"Destroying the VM")
        ccs.destroy_vm(my_vm)

        # Doing it again, checking that we get an exception
        try:
            ccs.destroy_vm(my_vm)
            raise wrench.WRENCHException("Should not be able to destroy a VM twice")
        except wrench.WRENCHException as e:
            pass

        try:
            print(f"VM Running: {my_vm.is_running()}")
            raise wrench.WRENCHException("Should not be able to query the state of a VM that's been destroyed")
        except wrench.WRENCHException as e:
            pass

        print("Terminating simulation daemon")
        simulation.terminate()

    except wrench.WRENCHException as e:
        print(f"Error: {e}")
        exit(1)
