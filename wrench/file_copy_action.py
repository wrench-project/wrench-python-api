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


class FileCopyAction(Action):
    """
    WRENCH File Copy Action class
    """

    def __init__(self, simulation, compound_job: CompoundJob, name: str, file: File,
                 src_storage_service: StorageService, dest_storage_service: StorageService, uses_scratch: bool) -> None:
        """
        Constructor
        :param simulation: simulation object
        :type simulation
        :param compound_job: compound job object
        :type compound_job: CompoundJob
        :param name: name of file copy action
        :type name: str
        :param file: name of file being copied
        :type file: File
        :param src_storage_service: source storage service being copied from
        :type src_storage_service: StorageService
        :param dest_storage_service: destination storage service being copied to
        :type dest_storage_service: StorageService
        :param uses_scratch: returns whether action uses scratch
        :type uses_scratch: bool

        """
        self.src_storage_service = src_storage_service
        self.dest_storage_service = dest_storage_service
        self.file = file
        self._uses_scratch = uses_scratch
        super().__init__(simulation, name, compound_job)

    def get_destination_file_location(self) -> StorageService:
        """
        Get destination storage service

        :return: destination storage service object
        :rtype: StorageService
        """
        return self.dest_storage_service

    def get_file(self) -> File:
        """
        Get file being copied

        :return: file object
        :rtype: File
        """
        return self.file

    def get_source_file_location(self) -> StorageService:
        """
        Get source storage service

        :return: source storage service object
        :rtype: StorageService
        """
        return self.src_storage_service

    def uses_scratch(self) -> bool:
        """
        Returns whether the action uses scratch

        :return: boolean on whether action uses scratch
        :rtype: boolean
        """
        return self._uses_scratch

    def __str__(self) -> str:
        """
        :return: String representation of the file copy action
        :rtype: str
        """
        s = f"File Copy Action {self._name}"
        return s

    def __repr__(self) -> str:
        """
        :return: String representation of the file copy action object
        :rtype: str
        """
        s = f"FileCopyAction(name={self._name})"
        return s
