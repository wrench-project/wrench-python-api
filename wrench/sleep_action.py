# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 The WRENCH Team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
from wrench.action import Action

class SleepAction(Action):
    """
    WRENCH Action class
    """
    def __init__(self, simulation, jobname: str, name: str, sleep_time: float) -> None:
        """
        Constructor

        :param simulation: simulation object
        :type simulation
        :param name: job name
        :type name: str
        :param name: action name
        :type name: str
        :param sleep_time: sleep time
        :type sleep_time: float
        """
        self.sleep_time = sleep_time
        super().__init__(simulation, jobname, name)

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
        s = f"Sleep Action {self.name}"
        return s

    def __repr__(self) -> str:
        """
        :return: String representation of the sleep action object
        :rtype: str
        """
        s = f"SleepAction(name={self.name})"
        return s
