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
from .file import File


class StorageService(SimulationItem):
    """
    WRENCH Storage Service class

    :param simulation: simulation object
    :type simulation: Simulation
    :param name: Storage service name
    :type name: str
    """

    def __init__(self, simulation, name: str) -> None:
        """
        Constructor
        """
        super().__init__(simulation, name)

    def create_file_copy(self, file: File) -> None:
        """
        Creates a copy of a file (ex nihilo) at this storage service
        :param file: the file
        :return:
        """
        return self.simulation.create_file_copy_at_storage_service(file.name, self.name)

    def __str__(self) -> str:
        """
        :return: String representation of the storage service
        :rtype: str
        """
        s = f"Storage Service {self.name}"
        return s

    def __repr__(self) -> str:
        """
        :return: String representation of the StorageService object
        :rtype: str
        """
        s = f"StorageService(name={self.name})"
        return s
