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

from wrench.file import File
from wrench.simulation_item import SimulationItem
from enum import Enum


if TYPE_CHECKING:  # pragma: no cover
    from wrench.workflow import Workflow
    from wrench.simulation import Simulation

from typing import List


class Task(SimulationItem):
    """
    WRENCH Task class
    """

    def __init__(self, simulation: Simulation, workflow: Workflow, name: str) -> None:
        """
        Constructor
        :param simulation: simulation object
        :type simulation: Simulation
        :param workflow: The workflow this task belongs to
        :type workflow: Workflow
        :param name: Task name
        :type name: str
        """
        self.workflow = workflow
        super().__init__(simulation, name)

    class TaskState(Enum):
        NOT_READY = 0
        READY = 1
        PENDING = 2
        COMPLETED = 3
        UNKNOWN = 4

    def get_state(self) -> TaskState:
        """
        Get the state of the action
        """
        return self.TaskState(self._simulation._task_get_state(self))

    def get_workflow(self) -> Workflow:
        """
        Get the task's workflow
        :rtype: Workflow
        """
        return self.workflow

    def add_input_file(self, file: File) -> None:
        """
        Add a file as input file for this task
        :param file: File name
        :type file: File
        """
        return self._simulation._add_input_file(self, file)

    def add_output_file(self, file: File) -> None:
        """
        Add a file as output file for this task
        :param file: File name
        :type file: File
        """
        return self._simulation._add_output_file(self, file)

    def get_input_files(self) -> List[File]:
        """
        Get the list of input files for this task
        :return: List of input file names
        :rtype: List[File]
        """
        return self._simulation._get_task_input_files(self)

    def get_output_files(self) -> List[File]:
        """
        Get the list of output files for this task
        :return: List of output file names
        :rtype: List[File]
        """
        return self._simulation._get_task_output_files(self)

    def get_flops(self) -> float:
        """
        Get the number of flops in a task
        :return: A number of flops
        :rtype: float
        """
        return self._simulation._task_get_flops(self)

    def get_min_num_cores(self) -> int:
        """
        Get the task's minimum number of required cores
        :return: A number of cores
        :rtype: integer
        """
        return self._simulation._task_get_min_num_cores(self)

    def get_max_num_cores(self) -> int:
        """
        Get the task's maximum number of required cores
        :return: A number of cores
        :rtype: integer
        """
        return self._simulation._task_get_max_num_cores(self)

    def get_memory(self) -> int:
        """
        Get the task's memory requirement
        :return: A memory size in bytes
        :rtype: int
        """
        return self._simulation._task_get_memory(self)

    def get_number_of_children(self) -> int:
        """
        Get the task's number of children
        :return: A number of children
        :rtype: int
        """
        return self._simulation._task_get_number_of_children(self)

    def get_bottom_level(self) -> int:
        """
        Get the task's bottom-level
        :return: A bottom-level
        :rtype: int
        """
        return self._simulation._task_get_bottom_level(self)

    def get_start_date(self) -> float:
        """
        Get the task's start date
        :return: A date in seconds
        :rtype: float
        """
        return self._simulation._task_get_start_date(self)

    def get_end_date(self) -> float:
        """
        Get the task's end date
        :return: A date in seconds
        :rtype: float
        """
        return self._simulation._task_get_end_date(self)

    def __str__(self) -> str:
        """
        String representation of the task when using print

        :return: String representation of the task
        :rtype: str
        """
        text_flops = "FLOPS"
        text_min_num_cores = "Minimum cores"
        text_max_num_cores = "Maximum cores"
        text_memory = "Memory requirement"

        sep = ''
        offset = ' '

        s = f"Task {self._name}:\n"
        s += f"{offset}{text_flops:<18}{sep}{self.get_flops():10.2f}\n"
        s += f"{offset}{text_min_num_cores:<18}{sep}{self.get_min_num_cores():10d}\n"
        s += f"{offset}{text_max_num_cores:<18}{sep}{self.get_max_num_cores():10d}\n"
        s += f"{offset}{text_memory:<18}{sep}{self.get_memory():10.2f}\n"

        return s

    def __repr__(self) -> str:
        """
        String representation of the Task object

        :return: String representation of the Task object
        :rtype: str
        """
        s = f"Task(name={self._name}, " + \
            f"flops={self.get_flops()}, " + \
            f"min_num_cores={self.get_min_num_cores()}, " + \
            f"max_num_cores={self.get_max_num_cores()}, " + \
            f"memory={self.get_memory()})"
        return s
