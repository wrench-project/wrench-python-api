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


class File(SimulationItem):
    """
    WRENCH File class

    :param simulation: simulation object
    :type simulation: Simulation
    :param name: Task name
    :type name: str
    """

    def __init__(self, simulation, name: str) -> None:
        """
        Constructor
        """
        super().__init__(simulation, name)

    def get_size(self) -> int:
        """
        Get the number of bytes of a file
        :return: Number of bytes of a file
        :rtype: int
        """
        return self.simulation.file_get_size(self.name)

    def __str__(self) -> str:
        """
        String representation of a file when using print
        
        :return: String representation of the task
        :rtype: str
        """
        s = f'File {self.name} of {self.get_size()} bytes'
        return s

    def __repr__(self) -> str:
        """
        String representation of a File object
        
        :return: String representation of a File object
        :rtype: str
        """
        s = f'File(name={self.name}, size={self.get_size()})'
        return s
