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
import sys

import wrench

if __name__ == "__main__":

    current_dir = pathlib.Path(__file__).parent.resolve()
    platform_file_path = pathlib.Path(current_dir / "sample_platform.xml")

    simulation = wrench.Simulation()
    with open(platform_file_path, "r") as platform_file:
        xml_string = platform_file.read()
    try:
        simulation.start(xml_string, "ControllerHost")
    except wrench.WRENCHException as e:
        sys.stderr.write(f"Error: {e}\n")
        exit(1)

    try:
        simulation.create_cloud_compute_service("CloudHeadHost_BOGUS",
                                                      ["CloudHost1_BOGUS", "CloudHost2"],
                                                      "/scratch",
                                                      {"CloudComputeServiceProperty::VM_BOOT_OVERHEAD": "5s"},
                                                      {"ServiceMessagePayload::STOP_DAEMON_MESSAGE_PAYLOAD": 1024})
        raise wrench.WRENCHException("Shouldn't be able to create bogus cloud compute service")
    except wrench.WRENCHException as e:
        pass

    ccs = simulation.create_cloud_compute_service("CloudHeadHost",
                                                  ["CloudHost1", "CloudHost2"],
                                                  "/scratch",
                                                  {"CloudComputeServiceProperty::VM_BOOT_OVERHEAD": "5s"},
                                                  {"ServiceMessagePayload::STOP_DAEMON_MESSAGE_PAYLOAD": 1024})

    # Coverage
    ccs.get_name()
    str(ccs)
    repr(ccs)

    assert not ccs.supports_compound_jobs(), "CS should support compound jobs"
    assert not ccs.supports_pilot_jobs(), "CS should support pilot jobs"
    assert not ccs.supports_standard_jobs(), "CS should support standard jobs"

    try:
        bogus_my_vm = ccs.create_vm(1000, 100,
                                    {"CloudComputeServiceProperty::VM_BOOT_OVERHEAD": "5s"},
                                    {"ServiceMessagePayload::STOP_DAEMON_MESSAGE_PAYLOAD": 1024})
        raise wrench.WRENCHException("Should not be able to create a crazy VM")
    except wrench.WRENCHException as e:
        pass

    my_vm = ccs.create_vm(1, 100,
                          {"CloudComputeServiceProperty::VM_BOOT_OVERHEAD": "5s"},
                          {"ServiceMessagePayload::STOP_DAEMON_MESSAGE_PAYLOAD": 1024})
    my_vm.get_name()
    str(my_vm)
    repr(my_vm)

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

    if not my_vm.is_running():
        raise wrench.WRENCHException("VM should be running")
    if my_vm.is_down():
        raise wrench.WRENCHException("VM should not be down")
    if my_vm.is_suspended():
        raise wrench.WRENCHException("VM should not be suspended")

    my_vm.suspend()
    if not my_vm.is_suspended():
        raise wrench.WRENCHException("VM should be suspended")

    my_vm.resume()
    if not my_vm.is_running():
        raise wrench.WRENCHException("VM should be running")

    workflow = simulation.create_workflow()
    task1 = workflow.add_task("task1", 10000000000.0, 1, 1, 0)
    job = simulation.create_standard_job([task1], {})
    vm_cs.submit_standard_job(job)
    event = simulation.wait_for_next_event()

    my_vm.shutdown()
    if not my_vm.is_down():
        raise wrench.WRENCHException("VM should be down")

    # Doing it again, checking that we get an exception
    try:
        my_vm.shutdown()
        raise wrench.WRENCHException("Should not be able to shutdown a VM twice")
    except wrench.WRENCHException as e:
        pass

    vm_cs = my_vm.start()
    if not my_vm.is_running():
        raise wrench.WRENCHException("VM should be running")

    task2 = workflow.add_task("task2", 10000000000.0, 1, 1, 0)

    # Bogus job submission
    try:
        bogus_job = simulation.create_standard_job([task2], {})
        ccs.submit_standard_job(bogus_job)
        raise wrench.WRENCHException("Should not be able to submit a standard job to a cloud compute service")
    except wrench.WRENCHException as e:
        pass

    # Bogus job submission
    try:
        bogus_cjob = simulation.create_compound_job("cjob")
        bogus_cjob.add_sleep_action("", 10)
        ccs.submit_compound_job(bogus_cjob)
        raise wrench.WRENCHException("Should not be able to submit a compound job to a cloud compute service")
    except wrench.WRENCHException as e:
        pass

    job = simulation.create_standard_job([task2], {})
    vm_cs.submit_standard_job(job)
    event = simulation.wait_for_next_event()

    my_vm.shutdown()
    if not my_vm.is_down():
        raise wrench.WRENCHException("VM should be down")

    ccs.destroy_vm(my_vm)

    # Doing it again, checking that we get an exception
    try:
        ccs.destroy_vm(my_vm)
        raise wrench.WRENCHException("Should not be able to destroy a VM twice")
    except wrench.WRENCHException as e:
        pass

    try:
        my_vm.is_running()
        raise wrench.WRENCHException("Should not be able to query the state of a VM that's been destroyed")
    except wrench.WRENCHException as e:
        pass

    simulation.terminate()
