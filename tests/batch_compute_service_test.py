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
import random

import wrench

if __name__ == "__main__":

    current_dir = pathlib.Path(__file__).parent.resolve()
    platform_file_path = pathlib.Path(current_dir / "sample_platform.xml")

    simulation = wrench.Simulation()
    try:
        simulation.start(platform_file_path, "ControllerHost")
    except wrench.WRENCHException as e:
        sys.stderr.write(f"Error: {e}\n")
        exit(1)

    try:
        bogus_cs = simulation.create_batch_compute_service(
            "BatchHeadHost",
            ["BatchHost1", "CloudHost2"],
            "/scratch",
            {},
            {"ServiceMessagePayload::STOP_DAEMON_MESSAGE_PAYLOAD": 1024.0})
        raise wrench.WRENCHException("Shouldn't be able to create a bogus batch compute service")
    except wrench.WRENCHException as e:
        pass

    cs = simulation.create_batch_compute_service(
        "BatchHeadHost",
        ["BatchHost1", "BatchHost2"],
        "/scratch",
        {},
        {"ServiceMessagePayload::STOP_DAEMON_MESSAGE_PAYLOAD": 1024.0})

    # Coverage
    cs.get_name()
    str(cs)
    repr(cs)

    assert cs.supports_compound_jobs(), "CS should support compound jobs"
    assert cs.supports_pilot_jobs(), "CS should support pilot jobs"
    assert cs.supports_standard_jobs(), "CS should support standard jobs"

    ss = simulation.create_simple_storage_service("StorageHost", ["/"])

    workflow = simulation.create_workflow()
    file1 = simulation.add_file("file1", 1024)
    ss.create_file_copy(file1)
    file2 = simulation.add_file("file2", 1024)
    file3 = simulation.add_file("file3", 1024)

    task1 = workflow.add_task("task1", 10000000000, 1, 1, 0)
    task1.add_input_file(file1)
    task1.add_output_file(file2)
    task2 = workflow.add_task("task2", 200000000000, 1, 1, 0)
    task2.add_input_file(file2)
    task2.add_output_file(file3)

    job = simulation.create_standard_job([task1, task2], {})

    host = random.randint(1, 2)
    core = random.randint(1, 6)
    second = random.randint(5*60, 15*50)
    service_specific_args = {"-N": str(host), "-c": str(core), "-t":str(second)}

    cs.submit_standard_job(job, service_specific_args)

    event = simulation.wait_for_next_event()
    assert event["event_type"] == "standard_job_failure", "Was expecting a standard job failure event " \
                                                          "but instead got a: " + event["event_type"]

    job = simulation.create_standard_job([task1, task2], {file1: ss, file3: ss})
    cs.submit_standard_job(job, service_specific_args)
    event = simulation.wait_for_next_event()
    assert event["event_type"] == "standard_job_completion", "Was expecting a standard job completion event " \
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
    simulation.terminate()

