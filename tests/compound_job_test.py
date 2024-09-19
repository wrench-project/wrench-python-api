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

    # Instantiating the simulation based on a platform description file
    current_dir = pathlib.Path(__file__).parent.resolve()
    platform_file_path = pathlib.Path(current_dir / "sample_platform.xml")

    # Creating a new WRENCH simulation
    simulation = wrench.Simulation()

    # Starting the simulation, with this simulated process running on the host ControllerHost
    simulation.start(platform_file_path, "ControllerHost")

    # Creating a  compute services
    bmcs = simulation.create_bare_metal_compute_service(
        "CloudHeadHost",
        {"CloudHost1": (6, 10.0),
         "CloudHost2": (6, 12.0)},
        "/scratch",
        {"BareMetalComputeServiceProperty::THREAD_STARTUP_OVERHEAD": "12s"},
        {"ServiceMessagePayload::STOP_DAEMON_MESSAGE_PAYLOAD": 1024.0})

    bcs = simulation.create_batch_compute_service(
        "BatchHeadHost",
        ["BatchHost1", "BatchHost2"],
        "/scratch",
        {},
        {"ServiceMessagePayload::STOP_DAEMON_MESSAGE_PAYLOAD": 1024.0})

    # Create two storage service
    ss1 = simulation.create_simple_storage_service("StorageHost", ["/"])
    ss2 = simulation.create_simple_storage_service("ControllerHost", ["/"])

    # Creating files
    file1 = simulation.add_file("file1", 1024)
    file2 = simulation.add_file("file2", 1024)

    # Adding a file to a storage service
    ss1.create_file_copy(file1)

    # Creating a compound job
    cj = simulation.create_compound_job("")
    cj.get_name()
    str(cj)
    repr(cj)

    # Add a file write action to compound job
    fwa = cj.add_file_write_action("FileWriteAction1", file1, ss1)
    fwa.get_name()
    str(fwa)
    repr(fwa)

    assert fwa.get_state() == wrench.Action.ActionState.READY, "FileWriteAction1 should be in the READY state"


    assert fwa.get_file() == file1, "FileWriteAction1 doesn't have the correct file"
    assert fwa.get_file_location() == ss1, "FileWriteAction1 doesn't have the correct file location"
    assert not fwa.uses_scratch(), "FileWriteAction1 doesn't have the correct use of scratch"

    # Add a file read action to compound job
    fra = cj.add_file_read_action("FileReadAction1", file1, ss1)
    cj.add_action_dependency(fwa, fra)
    fra.get_name()
    str(fra)
    repr(fra)

    assert fra.get_state() == wrench.Action.ActionState.NOT_READY, "FileReadAction1 should be in the READY state"


    assert fra.get_file() == file1, "FileReadAction1 doesn't have the correct file"
    assert fra.get_file_location() == ss1, "FileReadAction1 doesn't have the correct file location"
    assert fra.get_num_bytes_to_read() == file1.get_size(), "FileReadAction1 doesn't have the correct number of bytes"
    assert not fra.uses_scratch(), "FileReadAction1 doesn't have the correct use of scratch"

    # Add a file copy action to compound job
    fca = cj.add_file_copy_action("FileCopyAction1", file1, ss1, ss2)
    cj.add_action_dependency(fra, fca)
    fca.get_name()
    str(fca)
    repr(fca)

    assert fca.get_file() == file1, "FileCopyAction1 doesn't have the correct file"
    assert fca.get_source_file_location() == ss1, "FileCopyAction1 doesn't have the correct source file location"
    assert fca.get_destination_file_location() == ss2, "FileCopyAction1 doesn't have the correct dest file location"
    assert not fca.uses_scratch(), "FileCopyAction1 doesn't have the correct use of scratch"

    # Add a file delete action to compound job
    fda = cj.add_file_delete_action("FileDeleteAction1", file1, ss1)
    cj.add_action_dependency(fca, fda)
    fda.get_name()
    str(fda)
    repr(fda)

    assert fda.get_file() == file1, "FileDeleteAction1 doesn't have the correct file"
    assert fda.get_file_location() == ss1, "FileDeleteAction1 doesn't have the correct file location"
    assert not fda.uses_scratch(), "FileDeleteAction1 doesn't have the correct use of scratch"

    # Add a sleep action to compound job
    sa = cj.add_sleep_action("SleepAction1", 5.0)
    sa.get_name()
    str(sa)
    repr(sa)

    assert sa.get_sleep_time() == 5.0, "SleepAction1 doesn't have the correct sleeptime"

    # Add a compute action to compound job
    ca = cj.add_compute_action("ComputeAction1", 100.0, 0.0, 2, 1, ("AMDAHL", 0.8))
    ca.get_name()
    str(ca)
    repr(ca)

    assert ca.get_flops() == 100.0, "ComputeAction1 doesn't have the correct flops"
    assert ca.get_max_num_cores() == 2, "ComputeAction1 doesn't have the correct max cores"
    assert ca.get_min_num_cores() == 1, "ComputeAction1 doesn't have the correct min cores"
    assert ca.get_min_ram_footprint() == 0.0, "ComputeAction1 doesn't have the correct ram"
    assert ca.get_parallel_model() == ("AMDAHL", 0.8), "ComputeAction1 doesn't have the correct parallel model"

    actions = cj.get_actions()
    assert fwa in actions and fra in actions and fca in actions and fda in actions and \
           sa in actions and ca in actions, "Job's action list is invalid"

    # Add a parent compound job to another compound job
    cj2_0 = simulation.create_compound_job("")
    cj2_0.add_sleep_action("SleepAction2", 2.0)

    cj2_1 = simulation.create_compound_job("")
    cj2_1.add_sleep_action("SleepAction3", 2.0)

    cj2_1.add_parent_job(cj2_0)

    bmcs.submit_compound_job(cj2_0)
    bmcs.submit_compound_job(cj2_1)

    service_specific_args = {"-N": "1", "-c": "2", "-t": "60000"}
    bcs.submit_compound_job(cj, service_specific_args)

    event = simulation.wait_for_next_event()

    assert event["event_type"] == "compound_job_completion", f"Received an unexpected event: {event['event_type']}"

    event = simulation.wait_for_next_event()
    assert event["event_type"] == "compound_job_completion", f"Received an unexpected event: {event['event_type']}"

    event = simulation.wait_for_next_event()
    assert event["event_type"] == "compound_job_completion", f"Received an unexpected event: {event['event_type']}"

    assert ca.get_start_date() < ca.get_end_date(), "Incoherent ca start/end dates"

    assert not ca.get_failure_cause(), "ComputeAction1 should have a None failure cause"

    assert ca.get_state() == wrench.Action.ActionState.COMPLETED, "ComputeAction1 should be in the COMPLETED state"

    # Let's create a job that will fail
    cj3 = simulation.create_compound_job("")
    file4 = simulation.add_file("file4", 10)
    doomed = cj3.add_file_read_action("doomed", file4, ss1)
    bcs.submit_compound_job(cj3, service_specific_args)
    event = simulation.wait_for_next_event()

    assert event["event_type"] == "compound_job_failure", f"Received an unexpected event: {event['event_type']}"
    assert doomed.get_failure_cause() != "", f"Doomed action should have a failure cause"
    assert doomed.get_state() == wrench.Action.ActionState.FAILED, "Doomed should be in the FAILED state"
    simulation.terminate()
