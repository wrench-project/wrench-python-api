# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 The WRENCH Team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
from wrench.action import Action
from wrench.compound_job import CompoundJob
from wrench.file_registry_service import FileRegistryService
from wrench.file import File
from wrench.storage_service import StorageService


class FileRegistryAddEntryAction(Action):
    """
    WRENCH File Registry Add Entry Action class
    """
    def __init__(self, simulation, compound_job: CompoundJob, name: str, file_registry: FileRegistryService,
                 file: File, storage_service: StorageService, uses_scratch: bool) -> None:

        """
        Constructor

        :param simulation: simulation object
        :type simulation
        :param compound_job: compound job object
        :type compound_job: CompoundJob
        :param name: name of file write action
        :type name: str
        :param file: name of file to write
        :type file: File
        :param storage_service: storage service to write the file to
        :type storage_service: StorageService
        :param uses_scratch: returns whether action uses scratch
        :type uses_scratch: bool

        """
        self.storage_service = storage_service
        self.file = file
        self.uses_scratch = uses_scratch
        super().__init__(simulation, name, compound_job)

    def get_file(self) -> File:
        """
        Get file to write to

        :return: file object
        :rtype: File
        """
        return self.file

    def get_file_location(self) -> StorageService:
        """
        Get storage service of file to write to

        :return: storage service object
        :rtype: StorageService
        """
        return self.storage_service

    def uses_scratch(self) -> bool:
        """
        Returns whether the action uses scratch

        :return: boolean on whether action uses scratch
        :rtype: boolean
        """
        return self.uses_scratch

    def __str__(self) -> str:
        """
        :return: String representation of the file write action
        :rtype: str
        """
        s = f"File Write Action {self.name}"
        return s

    def __repr__(self) -> str:
        """
        :return: String representation of the file write action object
        :rtype: str
        """
        s = f"FileWriteAction(name={self.name})"
        return s
