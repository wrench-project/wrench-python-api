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

if TYPE_CHECKING:  # pragma: no cover
    from wrench.simulation import Simulation


# noinspection GrazieInspection
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
        self.size = None

    def get_size(self) -> int:
        """
        Get the file size in bytes

        :return: A number of bytes
        :rtype: int
        """
        if not self.size:
            self.size = self._simulation._file_get_size(self)
        return self.size;

    def __str__(self) -> str:
        """
        String representation of the file when using print
        
        :return: String representation of the file
        :rtype: str
        """
        s = f'File {self._name} of {self.get_size()} bytes'
        return s

    def __repr__(self) -> str:
        """
        String representation of the File object
        
        :return: String representation of the File object
        :rtype: str
        """
        s = f'File(name={self._name}, size={self.get_size()})'
        return s
