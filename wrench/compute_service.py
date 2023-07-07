#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 The WRENCH Team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from .simulation_item import SimulationItem
from .standard_job import StandardJob


class ComputeService(SimulationItem):
    """
    WRENCH Compute Service class
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

    def submit_standard_job(self, standard_job: StandardJob) -> None:
        """
        Submit a standard job to a compute service

        :param standard_job: the standard job
        :type standard_job: StandardJob
        """
        return self.simulation.submit_standard_job(standard_job.get_name(), self.name)

    def supports_compound_jobs(self) -> bool:
        """
        Returns true if the service supports compound jobs.
        :return:
        """
        return self.simulation.supports_compound_jobs(self.name)

    def supports_pilot_jobs(self) -> bool:
        """
        Returns true if the service supports pilot jobs.
        :return:
        """
        return self.simulation.supports_pilot_jobs(self.name)

    def supports_standard_jobs(self) -> bool:
        """
        Returns true if the service supports pilot jobs.
        :return:
        """
        return self.simulation.supports_standard_jobs(self.name)

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

    def __str__(self) -> str:
        """
        :return: String representation of a standard job
        :rtype: str
        """
        s = f"Compute Service {self.name}"
        return s

    def __repr__(self) -> str:
        """
        :return: String representation of a StandardJob object
        :rtype: str
        """
        s = f"ComputeService(name={self.name})"
        return s

