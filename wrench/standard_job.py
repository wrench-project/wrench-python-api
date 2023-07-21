#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 The WRENCH Team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from typing import List

from .simulation_item import SimulationItem
from .task import Task


class StandardJob(SimulationItem):
    """
    WRENCH Standard Job class
    """

    def __init__(self, simulation, name: str) -> None:
        """
        Constructor
        :param simulation: simulation object
        :type simulation
        :param name: Task name
        :type name: str
        """
        super().__init__(simulation, name)

    def get_tasks(self) -> List[Task]:
        """
        Get the number of tasks in a standard job

        :return: a list of task objects
        :rtype: List[Task]
        """
        return self.simulation._standard_job_get_tasks(self.name)
    
    def __str__(self) -> str:
        """
        :return: String representation of a standard job
        :rtype: str
        """
        s = f"Standard Job {self.name} with {len(self.get_tasks())} tasks"
        return s

    def __repr__(self) -> str:
        """
        :return: String representation of a StandardJob object
        :rtype: str
        """
        s = f"StandardJob(name={self.name})"
        return s
