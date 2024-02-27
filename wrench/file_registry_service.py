# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 The WRENCH Team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
from wrench.file import File
from wrench.storage_service import StorageService
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

    def add_entry(self, storage_service: StorageService, file: File):
        """
        Add an entry (file/storage service) to the file registry service
        :param file: the file
        :type file: File
        :param storage_service: the storage service
        :type storage_service: StorageService
        :return:
        """
        return self.simulation._add_entry_to_file_registry_service(self, file, storage_service)

    def remove_entry(self, storage_service: StorageService, file: File):
        """
        Removes an entry (file/storage service) from the file registry service
        :param file: the file
        :type file: File
        :param storage_service: the storage service
        :type storage_service: StorageService
        :return:
        """
        return self.simulation._remove_entry_to_file_registry_service(self, file, storage_service)

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
