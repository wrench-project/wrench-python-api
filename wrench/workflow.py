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

    def __init__(self, simulation) -> None:
        """
        Constructor
        :param simulation: simulation object
        :type simulation
        """
        super().__init__(simulation, "the_workflow")

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
        return self.simulation._workflow_create_task(name, flops, min_num_cores, max_num_cores, memory)

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

    def __str__(self) -> str:
        """
        String representation of a workflow when using print
        
        :return: String representation of the workflow
        :rtype: str
        """
        s = f'The workflow'
        return s

    def __repr__(self) -> str:
        """
        String representation of a Workflow object
        
        :return: String representation of a Workflow object
        :rtype: str
        """
        s = f'Workflow()'
        return s
