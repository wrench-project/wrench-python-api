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

class FileReadAction(Action):
    """
    WRENCH Action class
    """

    def __init__(self, simulation, compound_job: CompoundJob, name: str, file: File, storage_service: StorageService,
                 num_bytes_to_read: float, uses_scratch: bool) -> None:


        """
        Constructor
        :param simulation: simulation object
        :type simulation
        :param compound_job: compound job object
        :type compound_job: CompoundJob
        :param name: name of file read action
        :type name: str
        :param file: name of file being read
        :type file: File
        :param storage_service: storage service containing file
        :type storage_service: StorageService
        :param num_bytes_to_read: number of bytes to read
        :type num_bytes_to_read: float
        :param uses_scratch: whether action uses scratch
        :type uses_scratch: bool
        """
        self.file = file
        self.storage_service = storage_service
        self.num_bytes_to_read = num_bytes_to_read
        self.uses_scratch = uses_scratch
        super().__init__(simulation, name, compound_job)

    def get_file(self) -> File:
        """
        Get file being read
        :return: file
        :rtype: File
        """
        return self.file

    def get_file_location(self) -> StorageService:
        """
        Get storage service file is located in
        :return: storage service object
        :rtype: StorageService
        """
        return self.storage_service

    def get_num_bytes_to_read(self) -> float:
        """
        Get number of bytes to read from file
        :return: amount of bytes being read
        :rtype: float
        """
        return self.num_bytes_to_read

    def get_used_file_location(self) -> StorageService:
        """
        Get source storage service
        :return: source storage service object
        :rtype: StorageService
        """
        if (self.get_state() == self.ActionState.COMPLETED):
            return self.storage_service
        #throw exception?

    def uses_scratch(self) -> bool:
        """
        Returns whether the action uses scratch
        :return: boolean on whether action uses scratch
        :rtype: boolean
        """
        return self.uses_scratch

    def __str__(self) -> str:
        """
        :return: String representation of the file copy action
        :rtype: str
        """
        s = f"File Copy Action {self.name}"
        return s

    def __repr__(self) -> str:
        """
        :return: String representation of the file copy action object
        :rtype: str
        """
        s = f"FileCopyAction(name={self.name})"
        return s