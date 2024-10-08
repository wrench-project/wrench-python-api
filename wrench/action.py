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

    def __init__(self, simulation, name: str, compound_job: CompoundJob) -> None:
        """
        Constructor
        :param simulation: simulation object
        :type simulation
        :type name: str
        :param compound_job: compound job this action belongs to
        :type compound_job: CompoundJob
        """
        self.compound_job = compound_job
        super().__init__(simulation, name)

    """ This class HAS to match its corresponding C++ enum, which  
         is not great from a software maintenance standpoint, but makes things simple """

    class ActionState(Enum):
        NOT_READY = 0
        READY = 1
        STARTED = 2
        COMPLETED = 3
        KILLED = 4
        FAILED = 5

    def get_state(self) -> ActionState:
        """
        Get the state of the action
        """
        return self.ActionState(self._simulation._action_get_state(self))

    def get_job(self) -> CompoundJob:
        """
        Get the job that this task belongs to

        :return: a list of task objects
        :rtype: List[Task]
        """
        return self.compound_job

    def get_start_date(self) -> float:
        """
        Get the action's start date

        :return: a date (or -1 if not started)
        :rtype: float
        """
        return self._simulation._action_get_start_date(self)

    def get_end_date(self) -> float:
        """
        Get the action's end date

        :return: a date (or -1 if not ended)
        :rtype: float
        """
        return self._simulation._action_get_end_date(self)

    def get_failure_cause(self) -> str:
        """
        Get the action's failure cause

        :return: a failure cause (or None if no failure has occurred)
        :rtype: str
        """
        return self._simulation._action_get_failure_cause(self)

    def __str__(self) -> str:  # pragma: no cover
        """
        :return: String representation of the action
        :rtype: str
        """
        s = f"Action {self._name}"
        return s

    def __repr__(self) -> str:  # pragma: no cover
        """
        :return: String representation of the action object
        :rtype: str
        """
        s = f"Action(name={self._name})"
        return s
