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
import sys
import json

import wrench

if __name__ == "__main__":

    try:
        current_dir = pathlib.Path(__file__).parent.resolve()
        platform_file_path = pathlib.Path(current_dir / "sample_platform.xml")
        json_workflow_file_path = pathlib.Path(current_dir / "sample_wfcommons_workflow.json")

        simulation = wrench.Simulation()
        simulation.start(platform_file_path, "ControllerHost")

        workflow1 = simulation.create_workflow()
        print("Adding a a 1kB file to the simulation...")
        file1 = simulation.add_file("file1", 1024)
        print(f"Created file {file1}")
        print("Adding another 1kB file to the simulation...")
        file2 = simulation.add_file("file2", 2048)
        print(f"Created file {file2}")
        print("Adding another 1kB file to the simulation...")
        file3 = simulation.add_file("file3", 10000)
        print(f"Created file {file3}")

        print(f"The files in the simulation are {simulation.get_all_files()}")

        print("Creating a task")
        task1 = workflow1.add_task("task1", 100.0, 1, 8, 1024)
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

        print("Creating another task")
        task2 = workflow1.add_task("task2", 1000.0, 4, 4, 0)
        print(f"Just created a task with flops={task2.get_flops()}" +
              f", min_num_cores={task2.get_min_num_cores()}" +
              f", max_num_cores={task2.get_max_num_cores()}" +
              f", memory={task2.get_memory()}")

        task2.add_input_file(file2)
        print(f"Attached file {file2} as input file to task {task2.get_name()}")
        print(f"The list of input files for task {task2.get_name()} is: {task2.get_input_files()}")
        task2.add_output_file(file3)
        print(f"Attached file {file3} as output file to task {task2.get_name()}")
        print(f"The list of output files for task {task2.get_name()} is: {task2.get_output_files()}")

        print(f"The tasks in the workflow are: {workflow1.get_tasks()}")

        print("Creating a standard job with both tasks")
        job = simulation.create_standard_job([task1, task2], {})
        print(f"Created standard job has name {job.get_name()}")

        print(f"This job contains the following tasks: {job.get_tasks()}")

        print(f"Creating workflow from JSON")
        f = open(json_workflow_file_path)
        wfcommons_json_workflow = json.load(f)
        f.close()
        workflow2 = simulation.create_workflow_from_json(wfcommons_json_workflow, "2", False,
                                                                False,
                                                                False, 3.0, 3.0, False,
                                                                False, False)
        print(f"{workflow2}")
        print(f"The imported workflow from JSON has {len(workflow2.get_tasks())} tasks")
        print(f"One of its tasks is: {workflow2.get_tasks()[next(iter(workflow2.get_tasks()))]}")

        print("Terminating simulation daemon")
        simulation.terminate()

    except wrench.WRENCHException as e:
        print(f"Error: {e}")
        exit(1)
