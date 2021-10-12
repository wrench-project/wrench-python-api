#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 The WRENCH Team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from .simulation_item import SimulationItem


class Task(SimulationItem):
    """
    WRENCH Task class

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

    def __str__(self) -> str:
        """
        String representation of a task when using print
        
        :return: String representation of the task
        :rtype: str
        """
        text_flops = "FLOPS"
        text_min_num_cores = "Minimum cores" 
        text_max_num_cores = "Maximum cores" 
        text_memory = "Memory requirement"

        sep = ''
        offset = ' '

        s  = f"Task {self.name}:\n"
        s += f"{offset}{text_flops:<18}{sep}{self.get_flops():10.2f}\n"
        s += f"{offset}{text_min_num_cores:<18}{sep}{self.get_min_num_cores():10d}\n"
        s += f"{offset}{text_max_num_cores:<18}{sep}{self.get_max_num_cores():10d}\n"
        s += f"{offset}{text_memory:<18}{sep}{self.get_memory():10.2f}\n"

        return s

    def __repr__(self) -> str:
        """
        String representation of a Task object
        
        :return: String representation of a Task object
        :rtype: str
        """
        s = f"Task(name={self.name}, " + \
            f"flops={self.get_flops()}, " + \
            f"min_num_cores={self.get_min_num_cores()}, " + \
            f"max_num_cores={self.get_max_num_cores()}, " + \
            f"memory={self.get_memory()})"
        return s

    def get_flops(self) -> float:
        """
        Get the number of flops in a task
        """
        return self.simulation.task_get_flops(self.name)

    def get_min_num_cores(self) -> int:
        """
        Get the task's minimum number of required cores
        """
        return self.simulation.task_get_min_num_cores(self.name)

    def get_max_num_cores(self) -> int:
        """
        Get the task's maximum number of required cores
        """
        return self.simulation.task_get_max_num_cores(self.name)

    def get_memory(self) -> int:
        """
        Get the task's memory requirement
        """
        return self.simulation.task_get_memory(self.name)
