# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 The WRENCH Team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from __future__ import annotations

from wrench.simulation_item import SimulationItem
from wrench.file import File
from wrench.storage_service import StorageService

from typing import List
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wrench.compound_job import CompoundJob

class CompoundJob(SimulationItem):
    """
    WRENCH Action class
    """
    def __init__(self, simulation, name: str) -> None:
        """
        Constructor

        :param simulation: simulation object
        :type simulation
        :param name: name of compound job
        :type name: str
        """
        self.actions = []
        super().__init__(simulation, name)

    def get_actions(self) -> List:
        """
        Get the list of tasks in the job

        :return: a list of task objects
        :rtype: List[Task]
        """
        return self.actions

    def add_compute_action(self, name: str, flops: float, ram: float,
                         max_num_cores: int, min_num_cores: int, parallel_model: tuple):
        """
        Add a sleep action to the compound job
        :param name: name of compute action
        :type name: str
        :param flops: flops associated with this action
        :type flops: float
        :param ram : minimum amount of ram needed
        :type ram: float
        :param ram : minimum amount of ram needed
        :param min_num_cores: minimum amount of cores this action needs
        :type min_num_cores: int
        :param max_num_cores: maximum amount of cores this action can use
        :type max_num_cores: int
        :param parallel_model: type of parallel model and settings for it
        :type parallel_model: tuple
        """
        return self.simulation._add_compute_action(self, name, flops, ram, max_num_cores, min_num_cores, parallel_model)

    def add_file_copy_action(self, name: str, file: File, src_storage_service: StorageService,
                          dest_storage_service: StorageService):
        """
        Add a file copy action to the compound job
        :param name: name of file copy action
        :type name: str
        :param file: name of file being copied
        :type file: File
        :param src_storage_service: source storage service being copied from
        :type src_storage_service: StorageService
        :param dest_storage_service: destination storage service being copied to
        :type dest_storage_service: StorageService
        """
        return self.simulation._add_file_copy_action(self, name, file, src_storage_service, dest_storage_service)

    def add_file_delete_action(self, name: str, file: File, storage_service: StorageService):
        """
        Add a file delete action to the compound job
        :param name: name of file delete action
        :type name: str
        :param file: name of file being deleted
        :type file: File
        :param storage_service: storage service file is deleted from
        :type storage_service: StorageService
        """
        return self.simulation._add_file_delete_action(self, name, file, storage_service)

    def add_file_write_action(self, name: str, file: File, storage_service: StorageService):
        """
        Add a file write action to the compound job
        :param name: name of file write action
        :type name: str
        :param file: name of file to write
        :type file: File
        :param storage_service: storage service to write the file to
        :type storage_service: StorageService
        """
        return self.simulation._add_file_write_action(self, name, file, storage_service)

    def add_file_read_action(self, name: str, file: File, storage_service: StorageService,
                             num_bytes_to_read=-1.0):
        """
        Add a file write action to the compound job
        :param name: name of file write action
        :type name: str
        :param file: name of file to write
        :type file: File
        :param storage_service: storage service to write the file to
        :type storage_service: StorageService
        :param num_bytes_to_read: number of bytes to read in file
        :type num_bytes_to_read: float
        """
        return self.simulation._add_file_read_action(self, name, file, storage_service, num_bytes_to_read)

    def add_sleep_action(self, name: str, sleep_time: float):
        """
        Add a sleep action to the compound job
        :param name: name of the sleep action
        :type name: str
        :param sleep_time: the time to sleep
        :type sleep_time: float
        :return:
        """
        return self.simulation._add_sleep_action(self, name, sleep_time)

    def add_parent_job(self, parent_compound_job: CompoundJob):
        """
        Add a parent compound job to this compound job
        :param parent_compound_job: name of parent compound job
        :type parent_compound_job: CompoundJob
        :return:
        """
        return self.simulation._add_parent_job(self, parent_compound_job)

    def __str__(self) -> str:
        """
        :return: String representation of the storage service
        :rtype: str
        """
        s = f"Compound Job {self.name}"
        return s

    def __repr__(self) -> str:
        """
        :return: String representation of the FileRegistryService object
        :rtype: str
        """
        s = f"CompoundJob(name={self.name})"
        return s
