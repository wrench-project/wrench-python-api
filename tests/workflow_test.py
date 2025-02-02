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
import json
import sys

import wrench

if __name__ == "__main__":

    current_dir = pathlib.Path(__file__).parent.resolve()
    platform_file_path = pathlib.Path(current_dir / "sample_platform.xml")
    json_workflow_file_path = pathlib.Path(current_dir / "sample_wfcommons_workflow.json")

    simulation = wrench.Simulation()

    with open(platform_file_path, "r") as platform_file:
        bogus_xml_string = platform_file.read() + "BOGUS"
    try:
        simulation_bogus = wrench.Simulation()
        simulation_bogus.start(bogus_xml_string, "ControllerHost")
        raise wrench.WRENCHException("Should be able to start a simulation with a bogus xml")
    except wrench.WRENCHException as e:
        pass

    with open(platform_file_path, "r") as platform_file:
        xml_string = platform_file.read()
    try:
        simulation_bogus = wrench.Simulation()
        simulation_bogus.start(xml_string, "ControllerHost_BOGUS")
        raise wrench.WRENCHException("Should be able to start a simulation with a bogus xml file")
    except wrench.WRENCHException as e:
        pass

    simulation.start(xml_string, "ControllerHost")
    # Bogus restart that does nothing
    simulation.start(xml_string, "ControllerHost")

    workflow1 = simulation.create_workflow()
    file1 = simulation.add_file("file1", 1024)
    file2 = simulation.add_file("file2", 2048)
    file3 = simulation.add_file("file3", 10000)

    task1 = workflow1.add_task("task1", 100.0, 1, 8, 1024)

    if workflow1.get_ready_tasks() != [task1]:
        raise wrench.WRENCHException("The list of ready tasks is invalid (should be [task1])")

    task1.add_input_file(file1)
    task1.add_output_file(file2)

    bogus_file = simulation.add_file("bogus", 1)
    bogus_file._name = "really_bogus"
    try:
        task1.add_input_file(bogus_file)
        raise wrench.WRENCHException("Shouldn't be able to add bogus file as input to a task")
    except wrench.WRENCHException as e:
        pass

    try:
        task1.add_output_file(bogus_file)
        raise wrench.WRENCHException("Shouldn't be able to add bogus file as input to a task")
    except wrench.WRENCHException as e:
        pass

    if workflow1.is_done():
        raise wrench.WRENCHException("The workflow should not be done")

    task2 = workflow1.add_task("task2", 1000.0, 4, 4, 0)

    task2.add_input_file(file2)
    task2.add_output_file(file3)

    assert task1.get_number_of_children() == 1, "Task1 should have one child"
    assert task2.get_number_of_children() == 0, "Task2 should have zero children"
    assert task1.get_bottom_level() == 1, "Task1 should have bottom-level 1"
    assert task2.get_bottom_level() == 0, "Task2 should have bottom-level 0"

    if task1 not in workflow1.get_ready_tasks():
        raise wrench.WRENCHException("task1 should be ready")
    if task2 in workflow1.get_ready_tasks():
        raise wrench.WRENCHException("task2 should not be ready")
    if len(workflow1.get_ready_tasks()) != 1:
        raise wrench.WRENCHException("There should be 1 ready tasks")

    f = open(json_workflow_file_path)
    wfcommons_json_workflow = json.load(f)
    f.close()
    workflow2 = simulation.create_workflow_from_json(wfcommons_json_workflow, "2", False,
                                                     False,
                                                     False, 3, 3, False,
                                                     False, False)

    simulation.terminate()

    with open(platform_file_path, "r") as platform_file:
        xml_string = platform_file.read()
    try:
        simulation.start(xml_string, "ControllerHost")
        raise wrench.WRENCHException("Shouldn't be able to restart a simulation")
    except wrench.WRENCHException as e:
        pass


