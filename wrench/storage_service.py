# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 The WRENCH Team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from wrench.file import File
from wrench.simulation_item import SimulationItem


# noinspection GrazieInspection
class StorageService(SimulationItem):
    """
    WRENCH Storage Service class
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

    def create_file_copy(self, file: File) -> None:
        """
        Create a copy of a file (ex nihilo) at the storage service

        :param file: the file
        """
        return self._simulation._create_file_copy_at_storage_service(file, self)

    def lookup_file(self, file: File) -> bool:
        """
        Check whether a copy of a file is stored on the storage service

        :param file: the file
        :return: true or false
        :rtype: bool
        """
        return self._simulation._lookup_file_at_storage_service(file, self)

    def __str__(self) -> str:
        """
        :return: String representation of the storage service
        :rtype: str
        """
        s = f"Storage Service {self._name}"
        return s

    def __repr__(self) -> str:
        """
        :return: String representation of the StorageService object
        :rtype: str
        """
        s = f"StorageService(name={self._name})"
        return s
