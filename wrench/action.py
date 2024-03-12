# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 The WRENCH Team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
from wrench.file import File
from wrench.storage_service import StorageService
from wrench.simulation_item import SimulationItem
from wrench.file import File
from wrench.storage_service import StorageService

from typing import List


class Action(SimulationItem):
    """
    WRENCH Action class
    """
    def __init__(self, simulation, name: str, jobname: str) -> None:
        """
        Constructor

        :param simulation: simulation object
        :type simulation
        :param name: Job name
        :type name: str
        :param tasks: List of tasks in the job
        :type tasks: List[Task]
        """
        self.jobname = jobname
        super().__init__(simulation, name)

    def get_job(self) -> str:
        """
        Get the job

        :return: a list of task objects
        :rtype: List[Task]
        """
        return self.jobname

    def get_name(self) -> str:
        """
        Get the list of tasks in the job

        :return: a list of task objects
        :rtype: List[Task]
        """
        return self.name

    def __str__(self) -> str:
        """
        :return: String representation of the action
        :rtype: str
        """
        s = f"Action {self.name}"
        return s

    def __repr__(self) -> str:
        """
        :return: String representation of the action object
        :rtype: str
        """
        s = f"Action(name={self.name})"
        return s
