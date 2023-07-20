#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 The WRENCH Team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from .compute_service import ComputeService
from .virtual_machine import VirtualMachine


class CloudComputeService(ComputeService):
    """
    WRENCH Cloud Compute Service class
    """

    def __init__(self, simulation, name: str) -> None:
        """
        Constructor
        :param simulation: simulation object
        :type simulation
        :param name: Compute service name
        :type name: str
        """
        super().__init__(simulation, name)

    def create_vm(self, num_cores, ram_memory, property_list, message_payload_list) -> VirtualMachine:
        """
        Create a new virtual machine instance on a cloud compute service

        :param num_cores: number of cores in the virtual machine
        :type num_cores: int
        :param ram_memory: RAM size in bytes
        :type ram_memory: int
        :param property_list: a property list ({} means “use all defaults”)
        :type property_list: dict
        :param message_payload_list: a message payload list ({} means “use all defaults”)
        :type message_payload_list: dict
        :return: a VirtualMachine object
        :rtype: VirtualMachine
        """
        return self.simulation.create_vm(self.name, num_cores, ram_memory, property_list, message_payload_list)

    def destroy_vm(self, vm: VirtualMachine) -> None:
        """
        Create a new virtual machine instance on a cloud compute service

        :param vm: A virtual machine
        :type vm: VirtualMachine
        """
        return self.simulation.destroy_vm(self.name, vm.get_name())

    def __str__(self) -> str:
        """
        :return: String representation of a cloud compute service
        :rtype: str
        """
        s = f"Compute Service {self.name}"
        return s

    def __repr__(self) -> str:
        """
        :return: String representation of a CloudComputeService object
        :rtype: str
        """
        s = f"ComputeService(name={self.name})"
        return s
