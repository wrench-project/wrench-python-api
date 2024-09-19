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
    try:
        simulation.start(platform_file_path, "ControllerHost")
    except wrench.WRENCHException as e:
        sys.stderr.write(f"Error: {e}\n")
        exit(1)

    workflow = simulation.create_workflow()
    workflow.get_name()
    str(workflow)
    repr(workflow)

    file1 = simulation.add_file("file1", 1024)
    file1.get_name()
    str(file1)
    repr(file1)
    
    assert file1.get_size() == 1024, "File1 has an incorrect size"
    file2 = simulation.add_file("file2", 2048)
    try:
        invalid_file = simulation.add_file("file2", 1)
        raise wrench.WRENCHException("Shouldn't be able to add an already-existing file to the simulation")
    except wrench.WRENCHException as e:
        pass
    file3 = simulation.add_file("file3", 10000)

    files = simulation.get_all_files()
    assert files[file1.get_name()] == file1, "File1 should be known to the simulation"
    assert files[file2.get_name()] == file2, "File2 should be known to the simulation"
    assert files[file3.get_name()] == file3, "File3 should be known to the simulation"

    task1 = workflow.add_task("task1", 100.0, 1, 8, 1024)
    str(task1)
    repr(task1)

    assert task1.get_name() == "task1", "Task1 has an incorrect name"
    assert task1.get_flops() == 100.0, "Task1 has an incorrect flops"
    assert task1.get_min_num_cores() == 1, "Task1 has an incorrect min num cores"
    assert task1.get_max_num_cores() == 8, "Task1 has an incorrect max num cores"
    assert task1.get_memory() == 1024, "Task1 has an incorrect ram footprint"

    task1.add_input_file(file1)
    assert file1 in task1.get_input_files(), "File1 should be input to Task1"
    task1.add_output_file(file2)
    assert file2 in task1.get_output_files(), "File1 should be output from Task1"

    task2 = workflow.add_task("task2", 1000.0, 4, 4, 0)
    task2.add_input_file(file2)
    task1.add_output_file(file3)

    assert workflow.get_tasks()[task1.get_name()] == task1, "Task1 should be in the workflow"
    assert workflow.get_tasks()[task2.get_name()] == task2, "Task2 should be in the workflow"

    assert workflow.get_input_files() == [file1], "The workflow's input files should only be File1"

    try:
        job = simulation.create_standard_job([task2], {})
        raise wrench.WRENCHException("Should not be able to create a job with non-completed parents not in job")
    except wrench.WRENCHException as e:
        pass

    job = simulation.create_standard_job([task1, task2], {})
    str(job)
    repr(job)
    assert task1 in job.get_tasks(), "Task1 should be in job"
    assert task2 in job.get_tasks(), "Task2 should be in job"

    # Coverage
    task1._name = "BOGUS"
    try:
        task1.get_input_files()
        raise wrench.WRENCHException("Shouldb't be able to get the input files of a bogus task")
    except wrench.WRENCHException as e:
        pass
    try:
        task1.get_output_files()
        raise wrench.WRENCHException("Shouldb't be able to get the output files of a bogus task")
    except wrench.WRENCHException as e:
        pass
    try:
        task1.get_start_date()
        raise wrench.WRENCHException("Shouldn't be able to get the start date of a bogus task")
    except wrench.WRENCHException as e:
        pass
    try:
        task1.get_end_date()
        raise wrench.WRENCHException("Shouldn't be able to get the end date of a bogus task")
    except wrench.WRENCHException as e:
        pass
    try:
        task1.get_flops()
        raise wrench.WRENCHException("Shouldn't be able to get the flops of a bogus task")
    except wrench.WRENCHException as e:
        pass
    try:
        task1.get_memory()
        raise wrench.WRENCHException("Shouldn't be able to get the memory of a bogus task")
    except wrench.WRENCHException as e:
        pass
    try:
        task1.get_state()
        raise wrench.WRENCHException("Shouldn't be able to get the flops of a bogus task")
    except wrench.WRENCHException as e:
        pass
    try:
        task1.get_number_of_children()
        raise wrench.WRENCHException("Shouldn't be able to get the number of children of a bogus task")
    except wrench.WRENCHException as e:
        pass
    try:
        task1.get_bottom_level()
        raise wrench.WRENCHException("Shouldn't be able to get the bottom level of a bogus task")
    except wrench.WRENCHException as e:
        pass
    try:
        task1.get_min_num_cores()
        raise wrench.WRENCHException("Shouldn't be able to get the min num cores of a bogus task")
    except wrench.WRENCHException as e:
        pass
    try:
        task1.get_max_num_cores()
        raise wrench.WRENCHException("Shouldn't be able to get the max num cores of a bogus task")
    except wrench.WRENCHException as e:
        pass


    simulation.terminate()

