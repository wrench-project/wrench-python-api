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
from wrench.file import File
from wrench.storage_service import StorageService


class FileDeleteAction(Action):
    """
    WRENCH File Delete Action class
    """

    def __init__(self, simulation, compound_job: CompoundJob, name: str, file: File,
                 storage_service: StorageService, uses_scratch: bool) -> None:
        """
        Constructor
        :param simulation: simulation object
        :type simulation
        :param compound_job: compound job object
        :type compound_job: CompoundJob
        :param name: name of file delete action
        :type name: str
        :param file: name of file being deleted
        :type file: File
        :param storage_service: storage service file is deleted from
        :type storage_service: StorageService
        :param uses_scratch: returns whether action uses scratch
        :type uses_scratch: bool

        """
        self.storage_service = storage_service
        self.file = file
        self._uses_scratch = uses_scratch
        super().__init__(simulation, name, compound_job)

    def get_file(self) -> File:
        """
        Get file to delete

        :return: file object
        :rtype: File
        """
        return self.file

    def get_file_location(self) -> StorageService:
        """
        Get storage service file to delete is located in

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
        return self._uses_scratch

    def __str__(self) -> str:
        """
        :return: String representation of the file delete action
        :rtype: str
        """
        s = f"File Delete Action {self.name}"
        return s

    def __repr__(self) -> str:
        """
        :return: String representation of the file delete action object
        :rtype: str
        """
        s = f"FileDeleteAction(name={self.name})"
        return s
