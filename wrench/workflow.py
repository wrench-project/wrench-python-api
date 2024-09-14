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

if TYPE_CHECKING: # pragma: no cover
    from wrench.simulation import Simulation
    from wrench.task import Task
    from wrench.file import File
    from wrench.storage_service import StorageService
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
        Get the list of input files of the workflow

        :return: A dictionary of Task objects where task names are keys
        :rtype: List[File]
        """
        return self.simulation._workflow_get_input_files(self)

    def get_ready_tasks(self) -> List[Task]:
        """
        Get the list of ready tasks in the workflow

        :return: A list of Task objects
        :rtype: List[Task]
        """
        return self.simulation._workflow_get_ready_tasks(self)

    def is_done(self) -> bool:
        """
        Determine whether the workflow is done

        :return: True if the workflow is done, false otherwise
        :rtype: bool
        """
        return self.simulation._workflow_is_done(self)

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
