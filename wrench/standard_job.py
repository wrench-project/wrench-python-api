# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 The WRENCH Team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from typing import List

from wrench.simulation_item import SimulationItem
from wrench.task import Task


# noinspection GrazieInspection
class StandardJob(SimulationItem):
    """
    WRENCH Standard Job class
    """

    def __init__(self, simulation, name: str, tasks: List[Task]) -> None:
        """
        Constructor

        :param simulation: simulation object
        :type simulation
        :param name: Job name
        :type name: str
        :param tasks: List of tasks in the job
        :type tasks: List[Task]
        """
        self.tasks = tasks
        super().__init__(simulation, name)

    def get_tasks(self) -> List[Task]:
        """
        Get the list of tasks in the job

        :return: a list of task objects
        :rtype: List[Task]
        """
        return self.tasks

    def __str__(self) -> str:
        """
        :return: String representation of the standard job
        :rtype: str
        """
        s = f"Standard Job {self._name} with {len(self.tasks)} tasks"
        return s

    def __repr__(self) -> str:
        """
        :return: String representation of the StandardJob object
        :rtype: str
        """
        s = f"StandardJob(name={self._name})"
        return s
