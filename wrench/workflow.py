# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 The WRENCH Team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wrench.simulation import Simulation
    from wrench.task import Task
    from wrench.file import File
from wrench.simulation_item import SimulationItem

from typing import List
import json


# noinspection GrazieInspection
class Workflow(SimulationItem):
    """
    WRENCH Workflow class
    """

    def __init__(self, simulation: Simulation, name: str) -> None:
        """
        Constructor

        :param simulation: simulation object
        :type simulation
        :param name: the name of the workflow
        :type name: str
        """
        self.tasks = {}
        super().__init__(simulation, name)

    def add_task(self, name: str, flops: float, min_num_cores: int, max_num_cores: int, memory: float) -> Task:
        """
        Add a task to the workflow

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
        return self.simulation._workflow_create_task(self, name, flops, min_num_cores, max_num_cores, memory)

    def get_tasks(self) -> dict[str, Task]:
        """
        Get the tasks in the workflow

        :return: A dictionary of Task objects where task names are keys
        :rtype: dict[str, Task]
        """
        return self.tasks

    def get_input_files(self) -> List[File]:
        """
        Get all input files of the workflow

        :return: A dictionary of Task objects where task names are keys
        :rtype: List[File]
        """
        return self.simulation._workflow_get_input_files()

    def create_workflow_from_json(self, json_object: json, reference_flop_rate: str, ignore_machine_specs: bool,
                                  redundant_dependencies: bool, ignore_cycle_creating_dependencies: bool,
                                  min_cores_per_task: float, max_cores_per_task: float, enforce_num_cores: bool,
                                  ignore_avg_cpu: bool, show_warnings: bool) -> str:
        """
        Create a workflow from a WfCommons JSON

        :param json_object: A JSON object created from a WfCommons JSON file
        :type json_object: json
        :param reference_flop_rate: reference flop rate
        :type reference_flop_rate: str
        :param ignore_machine_specs: whether to ignore machine specifications in the JSON
        :type ignore_machine_specs: bool
        :param redundant_dependencies: whether to take into account redundant task dependencies
        :type redundant_dependencies: bool
        :param ignore_cycle_creating_dependencies: whether to ignore cycles when creating task dependencies
        :type ignore_cycle_creating_dependencies: bool
        :param min_cores_per_task: the minimum cores for a task if not specified in the JSON
        :type min_cores_per_task: float
        :param max_cores_per_task: the maximum cores for a task if not specified in the JSON
        :type max_cores_per_task: float
        :param enforce_num_cores: whether to enforce the number of cores for a task even if specified in the JSON
        :type enforce_num_cores: bool
        :param ignore_avg_cpu: whether to ignore the average CPU time information in the JSON to compute
               sequential task execution times
        :type ignore_avg_cpu: bool
        :param show_warnings: whether to show warnings when importing the JSON (displayed on the wrench-daemon console)
        :type show_warnings: bool

        :return: A Workflow
        :rtype: str
        """
        return self.simulation._create_workflow_from_json(json_object, reference_flop_rate, ignore_machine_specs,
                                                          redundant_dependencies, ignore_cycle_creating_dependencies,
                                                          min_cores_per_task, max_cores_per_task, enforce_num_cores,
                                                          ignore_avg_cpu, show_warnings)

    def __str__(self) -> str:
        """
        String representation of the workflow when using print
        
        :return: String representation of the workflow
        :rtype: str
        """
        s = f'Workflow ' + self.name
        return s

    def __repr__(self) -> str:
        """
        String representation of the Workflow object
        
        :return: String representation of the Workflow object
        :rtype: str
        """
        s = f"Workflow(name={self.name})"
        return s
