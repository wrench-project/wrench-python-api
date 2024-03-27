# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 The WRENCH Team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
from wrench.simulation_item import SimulationItem
from wrench.compound_job import CompoundJob
from enum import Enum

class Action(SimulationItem):
    """
    WRENCH Action class
    """
    class ActionState(Enum):
        NOT_READY = 0
        READY = 1
        STARTED = 2
        COMPLETED = 3
        KILLED = 4
        FAILED = 5

    def __init__(self, simulation, name: str, compound_job: CompoundJob) -> None:
        """
        Constructor

        :param simulation: simulation object
        :type simulation
        :param name: Job name
        :type name: str
        :param compound_job: compound job this action belongs to
        :type compound_job: CompoundJob
        """
        self.compound_job = compound_job
        super().__init__(simulation, name)

    def get_state(self) -> Enum:
        """
        Get the job

        :return: a list of task objects
        :rtype: List[Task]
        """
        return self.compound_job

    def get_state_as_string(self) -> str:
        """
        Get the job

        :return: a list of task objects
        :rtype: List[Task]
        """
        return self.compound_job

    def get_job(self) -> CompoundJob:
        """
        Get the job

        :return: a list of task objects
        :rtype: List[Task]
        """
        return self.compound_job

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
