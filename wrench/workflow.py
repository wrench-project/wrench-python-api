#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 The WRENCH Team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from .simulation_item import SimulationItem
from .task import Task

from typing import List


class Workflow(SimulationItem):
    """
    WRENCH Workflow class.
    """

    def __init__(self, simulation, name) -> None:
        """
        Constructor
        :param simulation: simulation object
        :type simulation
        :param name: the name of the workflow
        :type name: str
        """
        super().__init__(simulation, name)

    def add_task(self, workflow_name: str, name: str, flops: float, min_num_cores: int, max_num_cores: int, memory: float) -> Task:
        """
        Add a task to the workflow

        :param workflow_name: the name of the workflow
        :type workflow_name: str
        :param name: task name
        :type name: str
        :param flops: number of flops
        :type flops: float
        :param min_num_cores: minimum number of cores
        :type min_num_cores: int
        :param max_num_cores: maximum number of cores
        :type max_num_cores: int
        :param memory: memory requirement in bytes
        :type memory: float

        :return: A task object
        :rtype: Task

        :raises WRENCHException: if there is any error in the response
        """
        return self.simulation._workflow_create_task(workflow_name, name, flops, min_num_cores, max_num_cores, memory)

    def get_tasks(self) -> dict[str, Task]:
        """
        Get the list of all tasks in the workflow

        :return: A dictionary of Task objects where task names are keys
        :rtype: dict[str, Task]
        """
        return self.simulation._workflow_get_all_tasks()

    def get_input_files(self) -> List[str]:
        """
        Get the list of all input files of the workflow

        :return: A dictionary of Task objects where task names are keys
        :rtype: dict[str, Task]
        """
        return self.simulation._workflow_get_input_files()

    def create_workflow_from_json_string(self, json_string: str, reference_flop_rate: str, ignore_machine_specs: bool,
                                         redundant_dependencies: bool, ignore_cycle_creating_dependencies: bool, min_cores_per_task: float,
                                         max_cores_per_task: float, enforce_num_cores: bool, ignore_avg_cpu: bool, show_warnings: bool) -> str:
        """
        Return the status of the workflow simulator
        :return: A str value if the workflow succeeds.
        :rtype: str
        """
        return self.simulation._create_workflow_from_json_string(json_string, reference_flop_rate, ignore_machine_specs,
                                                                redundant_dependencies, ignore_cycle_creating_dependencies,
                                                                 min_cores_per_task, max_cores_per_task, enforce_num_cores,
                                                                 ignore_avg_cpu, show_warnings)

    def __str__(self) -> str:
        """
        String representation of a workflow when using print
        
        :return: String representation of the workflow
        :rtype: str
        """
        s = f'Workflow ' + self.name
        return s

    def __repr__(self) -> str:
        """
        String representation of a Workflow object
        
        :return: String representation of a Workflow object
        :rtype: str
        """
        s = f"Workflow(name={self.name})"
        return s
