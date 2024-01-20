#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 The WRENCH Team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from wrench.simulation_item import SimulationItem
from wrench.file import File


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
        Creates a copy of a file (ex nihilo) at this storage service

        :param file: the file
        :return
        """
        return self.simulation._create_file_copy_at_storage_service(file, self)

    def lookup_file(self, file: File) -> bool:
        """
        Checks whether a copy of a file is stored on the storage service

        :param file: the file
        :return true or false
        :rtype bool
        """
        return self.simulation._lookup_file_at_storage_service(file, self)

    def __str__(self) -> str:
        """
        :return String representation of the storage service
        :rtype str
        """
        s = f"Storage Service {self.name}"
        return s

    def __repr__(self) -> str:
        """
        :return String representation of the StorageService object
        :rtype str
        """
        s = f"StorageService(name={self.name})"
        return s
