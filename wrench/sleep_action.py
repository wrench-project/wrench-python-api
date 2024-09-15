# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 The WRENCH Team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
from wrench.action import Action
from wrench.compound_job import CompoundJob


class SleepAction(Action):
    """
    WRENCH Sleep Action class
    """

    def __init__(self, simulation, compound_job: CompoundJob, name: str, sleep_time: float) -> None:
        """
        Constructor
        :param simulation: simulation object
        :type simulation
        :param name: job name
        :type name: str
        :param name: name of sleep action
        :type name: str
        :param sleep_time: time to sleep
        :type sleep_time: float
        """
        self.sleep_time = sleep_time
        super().__init__(simulation, name, compound_job)

    def get_sleep_time(self) -> float:
        """
        Get sleep time

        :return: a sleep time
        :rtype: float
        """
        return self.sleep_time

    def __str__(self) -> str:
        """
        :return: String representation of the sleep action
        :rtype: str
        """
        s = f"Sleep Action {self._name}"
        return s

    def __repr__(self) -> str:
        """
        :return: String representation of the sleep action object
        :rtype: str
        """
        s = f"SleepAction(name={self._name})"
        return s
