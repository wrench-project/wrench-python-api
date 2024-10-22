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

    assert simulation.get_simulated_time() == 0, "The simulation time should be zero"

    assert sorted(simulation.get_all_hostnames()) == sorted(
        ["ControllerHost", "StorageHost", "CloudHeadHost", "CloudHost1", "CloudHost2", "BatchHeadHost",
         "BatchHost1", "BatchHost2"]), "Invalid list of hosts in the platform"

    try:
        bogus_cs = simulation.create_bare_metal_compute_service(
            "BatchHeadHost",
            {"BatchHostBOGUS": (6, 10.0),
             "BatchHost2": (6, 12.0)},
            "/scratch",
            {"BareMetalComputeServiceProperty::THREAD_STARTUP_OVERHEAD": "12s"},
            {"ServiceMessagePayload::STOP_DAEMON_MESSAGE_PAYLOAD": 1024.0})
    except wrench.WRENCHException as e:
        pass

    cs = simulation.create_bare_metal_compute_service(
        "BatchHeadHost",
        {"BatchHost1": (6, 10.0),
         "BatchHost2": (6, 12.0)},
        "/scratch",
        {"BareMetalComputeServiceProperty::THREAD_STARTUP_OVERHEAD": "12s"},
        {"ServiceMessagePayload::STOP_DAEMON_MESSAGE_PAYLOAD": 1024.0})

    # Coverage
    cs.get_name()
    str(cs)
    repr(cs)

    assert cs.supports_compound_jobs(), "CS should support compound jobs"
    assert not cs.supports_pilot_jobs(), "CS should not support pilot jobs"
    assert cs.supports_standard_jobs(), "CS should support standard jobs"

    core_counts = cs.get_core_counts()
    for entry in cs.get_core_counts():
        assert entry in ["BatchHost1", "BatchHost2"], "Invalid host in core counts"
        assert core_counts[entry] == 6, f"Invalid core count: {core_counts[entry]}"

    flop_rates = cs.get_core_flop_rates()
    for entry in flop_rates:
        assert entry in ["BatchHost1", "BatchHost2"], "Invalid host in flop rates"
        assert flop_rates[entry] == 10000000000.0, f"Invalid flop rate: {core_counts[entry]}"

    try:
        bogus_ss = simulation.create_simple_storage_service("StorageHost", ["/bogus"])
    except wrench.WRENCHException as e:
        pass

    ss = simulation.create_simple_storage_service("StorageHost", ["/"])

    workflow = simulation.create_workflow()
    workflow.get_name()

    file1 = simulation.add_file("file1", 1024)
    file1.get_name()
    ss.create_file_copy(file1)
    file2 = simulation.add_file("file2", 1024)
    file3 = simulation.add_file("file3", 1024)

    task1 = workflow.add_task("task1", 10000000000, 1, 1, 0)
    task1.get_name()
    task1.add_input_file(file1)
    task1.add_output_file(file2)
    task2 = workflow.add_task("task2", 200000000000, 1, 1, 0)
    task2.add_input_file(file2)
    task2.add_output_file(file3)

    assert task1.get_state() == wrench.Task.TaskState.READY, "task1 should be READY"
    assert task2.get_state() == wrench.Task.TaskState.NOT_READY, "task2 should be NOT_READY"

    job = simulation.create_standard_job([task1, task2], {})
    job.get_name()
    assert set(job.get_tasks()) == {task1, task2}, "Job tasks are incoherent"
    str(job)
    repr(job)

    cs.submit_standard_job(job)

    event = simulation.wait_for_next_event()
    assert event["event_type"] == "standard_job_failure", "Was expecting a standard job failure event " \
                                                          "but instead got a: " + event["event_type"]

    job = simulation.create_standard_job([task1, task2], {file1: ss, file3: ss})
    cs.submit_standard_job(job)
    event = simulation.wait_for_next_event()
    assert event["event_type"] == "standard_job_completion", f"Was expecting a standard job completion event " \
                                                             "but instead got a: " + event["event_type"]

    assert task1.get_start_date() < task1.get_end_date(), f"Incoherent task1 dates: " \
                                                          f"{task1.get_start_date()} and {task1.get_end_date()}"
    assert task2.get_start_date() < task2.get_end_date(), f"Incoherent task2 dates: " \
                                                          f"{task2.get_start_date()} and {task2.get_end_date()}"
    assert task1.get_end_date() <= task2.get_start_date(), f"task2 should have started after task1 ended"

    assert ss.lookup_file(file1), "File1 should be present in the storage service"
    assert not ss.lookup_file(file2), "File2 should not be present in the storage service"
    assert ss.lookup_file(file3), "File3 should be present in the storage service"

    assert workflow.is_done(), "The workflow should be done"

    # Trying a bogus job
    workflow1 = simulation.create_workflow()
    t1 = workflow1.add_task("task", 10.0, 1, 2, 0.0)
    workflow2 = simulation.create_workflow()
    t2 = workflow2.add_task("task", 10.0, 1, 2, 0.0)
    try:
        simulation.create_standard_job([t1, t2], {})
        raise wrench.WRENCHException("Shouldn't be able to create a job with tasks from different workflows")
    except wrench.WRENCHException as e:
        pass

    # Trying a job that is invalid
    workflow3 = simulation.create_workflow()
    t3 = workflow3.add_task("task", 10.0, 1, 1, 100000000000)
    job = simulation.create_standard_job([t3], {})
    try:
        cs.submit_standard_job(job)
        raise wrench.WRENCHException("Shouldn't be able to submit invalid job")
    except wrench.WRENCHException as e:
        pass

    # Trying a job that should fail
    workflow4 = simulation.create_workflow()
    t4 = workflow4.add_task("task", 10.0, 1, 1, 0)
    file4 = simulation.add_file("file4", 10)
    t4.add_input_file(file4)
    job = simulation.create_standard_job([t4], {file4: ss})
    cs.submit_standard_job(job)

    assert t4.get_state() == wrench.Task.TaskState.PENDING, "t4's state should be PENDING"

    event = simulation.wait_for_next_event()
    assert event["event_type"] == "standard_job_failure", "The job should have failed"

    assert t4.get_state() == wrench.Task.TaskState.READY, "t4's state should be READY"

    simulation.terminate()
