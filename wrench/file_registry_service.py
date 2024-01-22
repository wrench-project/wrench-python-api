# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 The WRENCH Team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from wrench.simulation_item import SimulationItem


class FileRegistryService(SimulationItem):
    """
    WRENCH File Registry Service class
    """

    def __init__(self, simulation, name: str) -> None:
        """
        Constructor
        :param simulation: simulation object
        :type simulation
        :param name: Storage service name
        :type name: str
        """
        super().__init__(simulation, name)

    def __str__(self) -> str:
        """
        :return: String representation of the storage service
        :rtype: str
        """
        s = f"File Registry Service {self.name}"
        return s

    def __repr__(self) -> str:
        """
        :return: String representation of the FileRegistryService object
        :rtype: str
        """
        s = f"FileRegistryService(name={self.name})"
        return s
