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
from wrench.storage_service import StorageService

from typing import List


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
        Add an entry (storage service / file) to the file registry service

        :param storage_service: a storage service
        :type storage_service: StorageService
        :param file: a file
        :type file: File
        :return:
        """
        self.simulation._add_entry_to_file_registry_service(self, file, storage_service)

    def lookup_entry(self, file: File) -> List[StorageService]:
        """
        Lookup an entry (file) to the file registry service

        :param file: a file
        :type file: File
        :return: List of StorageServices associated with file
        :rtype: str[]
        """
        return self.simulation._lookup_entry_in_file_registry_service(self, file)

    def remove_entry(self, storage_service: StorageService, file: File):
        """
        Removes an entry (file/storage service) from the file registry service

        :param file: a file
        :type file: File
        :param storage_service: a storage service
        :type storage_service: StorageService
        :return:
        """
        self.simulation._remove_entry_from_file_registry_service(self, file, storage_service)

    def __str__(self) -> str:
        """
        :return: String representation of the FileRegistryService service
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

