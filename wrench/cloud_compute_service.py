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
from .standard_job import StandardJob


class CloudComputeService(ComputeService):
    """
    WRENCH Cloud Compute Service class
    :param simulation: simulation object
    :type simulation: Simulation
    :param name: Compute service name
    :type name: str
    """

    def __init__(self, simulation, name: str) -> None:
        """
        Constructor
        """
        super().__init__(simulation, name)

    def create_vm(self, num_cores, ram_memory, property_list, message_payload_list) -> str:
        """
        Create a new VM instance on a cloud compute service

        :param num_cores: number of cores in the VM
        :type num_cores: int
        :param ram_memory: RAM size in bytes
        :type ram_memory: int
        :param property_list: a property list ({} means “use all defaults”)
        :type property_list: dict
        :param message_payload_list: a message payload list ({} means “use all defaults”)
        :type message_payload_list: dict
        :return: a VM name
        :rtype: str
        """
        return self.simulation.create_vm(self.name, num_cores, ram_memory, property_list, message_payload_list)

    def start_vm(self, vm_name):
        """
        Starts a VM and get the name of its associated bare metal compute service
        :param vm_name: name of the vm
        :type vm_name: str
        :return: a bare metal compute service name
        :rtype: str
        """
        return self.simulation.start_vm(self.name, vm_name)

    def shutdown_vm(self, vm_name):
        """
        Shutdowns a VM
        :param vm_name: name of the vm
        :type vm_name: str
        """
        self.simulation.shutdown_vm(self.name, vm_name)
        return

    def destroy_vm(self, vm_name):
        """
        Destroys a VM
        :param vm_name: name of the vm
        :type vm_name: str
        """
        self.simulation.destroy_vm(self.name, vm_name)
        return

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

