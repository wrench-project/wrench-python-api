# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 The WRENCH Team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
from wrench.simulation_item import SimulationItem
from wrench.sleep_action import SleepAction
from wrench.action import Action

from typing import List


class compound_job(SimulationItem):
    """
    WRENCH Action class
    """
    def __init__(self, simulation, name: str) -> None:
        """
        Constructor

        :param simulation: simulation object
        :type simulation
        :param name: Job name
        :type name: str
        :param tasks: List of tasks in the job
        :type tasks: List[Task]
        """
        self.actions = []
        super().__init__(simulation, name)

    def get_actions(self) -> List[Action]:
        """
        Get the list of tasks in the job

        :return: a list of task objects
        :rtype: List[Task]
        """
        return self.actions

    def addSleepAction(self, name: str, sleep_time: float) -> SleepAction:
        """
        Add an sleep action to the compound job
        :param name
        :type name: str
        :param sleep_time: the time to sleep
        :type sleep_time: float
        :return:
        """
        return self.simulation._add_sleep_action(self, name, sleep_time)

    def __str__(self) -> str:
        """
        :return: String representation of the storage service
        :rtype: str
        """
        s = f"Compound Job {self.name}"
        return s

    def __repr__(self) -> str:
        """
        :return: String representation of the FileRegistryService object
        :rtype: str
        """
        s = f"CompoundJob(name={self.name})"
        return s
