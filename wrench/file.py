#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 The WRENCH Team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.


from __future__ import annotations
from typing import TYPE_CHECKING

from wrench.simulation_item import SimulationItem

if TYPE_CHECKING:
    from wrench.simulation import Simulation


class File(SimulationItem):
    """
    WRENCH File class
    """

    def __init__(self, simulation: Simulation, name: str) -> None:
        """
        Constructor

        :param simulation: simulation object
        :type simulation: Simulation
        :param name: File name
        :type name: str
        """
        super().__init__(simulation, name)

    def get_size(self) -> int:
        """
        Get the file size in bytes

        :return: A number of bytes
        :rtype: int
        """
        return self.simulation._file_get_size(self)

    def __str__(self) -> str:
        """
        String representation of a file when using print
        
        :return: String representation of the file
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
