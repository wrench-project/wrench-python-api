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
from typing import Tuple
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    # from wrench.compound_job import CompoundJob
    from wrench.action import Action
    from wrench.compute_action import ComputeAction
    from wrench.file_copy_action import FileCopyAction
    from wrench.file_delete_action import FileDeleteAction
    from wrench.file_write_action import FileWriteAction
    from wrench.file_read_action import FileReadAction
    from wrench.sleep_action import SleepAction


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

    def get_actions(self) -> List[Action]:
        """
        Get the list of tasks in the job

        :return: a list of task objects
        :rtype: List[Task]
        """
        return self.actions

    def add_compute_action(self, name: str, flops: float, ram: float,
                           max_num_cores: int, min_num_cores: int, parallel_model: Tuple[str, float]) -> ComputeAction:
        """
        Add a sleep action to the compound job

        :param name: name of compute action
        :type name: str
        :param flops: flops associated with this action
        :type flops: float
        :param ram: minimum amount of ram needed
        :type ram: float
        :param min_num_cores: minimum amount of cores this action needs
        :type min_num_cores: int
        :param max_num_cores: maximum amount of cores this action can use
        :type max_num_cores: int
        :param parallel_model: type of parallel model and settings for it. Allowed types
        are "AMDAHL" or "CONSTANTEFFICIENCY", both of which take a float parameters between 0.0 and 1.0.
        The AMDAHL model's parameter denotes the fraction of the sequential execution time that is perfectly parallelizable.
        The CONSTANTEFFICIENCY model's parameter is simply the parallel efficiency. For instance, one could pass ("AMDAHL", 0.8).
        :type parallel_model: tuple
        """
        return self._simulation._add_compute_action(self, name, flops, ram, max_num_cores, min_num_cores, parallel_model)

    def add_file_copy_action(self, name: str, file: File, src_storage_service: StorageService,
                             dest_storage_service: StorageService) -> FileCopyAction:
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
        return self._simulation._add_file_copy_action(self, name, file, src_storage_service, dest_storage_service)

    def add_file_delete_action(self, name: str, file: File, storage_service: StorageService) -> FileDeleteAction:
        """
        Add a file delete action to the compound job

        :param name: name of file delete action
        :type name: str
        :param file: name of file being deleted
        :type file: File
        :param storage_service: storage service file is deleted from
        :type storage_service: StorageService
        """
        return self._simulation._add_file_delete_action(self, name, file, storage_service)

    def add_file_write_action(self, name: str, file: File, storage_service: StorageService) -> FileWriteAction:
        """
        Add a file write action to the compound job

        :param name: name of file write action
        :type name: str
        :param file: name of file to write
        :type file: File
        :param storage_service: storage service to write the file to
        :type storage_service: StorageService
        """
        return self._simulation._add_file_write_action(self, name, file, storage_service)

    def add_file_read_action(self, name: str, file: File, storage_service: StorageService,
                             num_bytes_to_read=-1.0) -> FileReadAction:
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
        return self._simulation._add_file_read_action(self, name, file, storage_service, num_bytes_to_read)

    def add_sleep_action(self, name: str, sleep_time: float) -> SleepAction:
        """
        Add a sleep action to the compound job

        :param name: name of the sleep action
        :type name: str
        :param sleep_time: the time to sleep
        :type sleep_time: float
        :return:
        """
        return self._simulation._add_sleep_action(self, name, sleep_time)

    def add_action_dependency(self, parent_action: Action, child_action: Action):
        """
        Add a dependency between two actions

        :param parent_action: the parent action
        :type parent_action: Action
        :param child_action: the child action
        :type child_action: Action
        :return:
        """
        return self._simulation._add_action_dependency(self, parent_action, child_action)

    def add_parent_job(self, parent_compound_job: CompoundJob):
        """
        Add a parent compound job to this compound job

        :param parent_compound_job: name of parent compound job
        :type parent_compound_job: CompoundJob
        :return:
        """
        return self._simulation._add_parent_job(self, parent_compound_job)

    def __str__(self) -> str:
        """
        :return: String representation of the compound job
        :rtype: str
        """
        s = f"Compound Job {self._name}"
        return s

    def __repr__(self) -> str:
        """
        :return: String representation of the CompoundJob object
        :rtype: str
        """
        s = f"CompoundJob(name={self._name})"
        return s
