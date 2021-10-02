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

    :param simulation: simulation object
    :type simulation: WRENCHSimulation
    :param name: Task name
    :type name: str
    """

    def __init__(self, simulation, name: str) -> None:
        """
        Constructor
        """
        super().__init__(simulation, name)

    def get_tasks(self) -> List[Task]:
        """
        Get the number of tasks in a standard job

        :return: a list of task objects
        :rtype: List[Task]
        """
        return self.simulation.standard_job_get_tasks(self.name)
