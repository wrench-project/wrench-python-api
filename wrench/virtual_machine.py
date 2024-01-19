#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 The WRENCH Team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from wrench.simulation_item import SimulationItem
from wrench.bare_metal_compute_service import BareMetalComputeService


class VirtualMachine(SimulationItem):
    """
    WRENCH Virtual Machine class.
    """

    def __init__(self, simulation, cloud_compute_service_name: str, name: str) -> None:
        """
        Constructor
        :param simulation: simulation object
        :type simulation
        :param cloud_compute_service_name: cloud compute service name
        :type cloud_compute_service_name: str
        :param name: virtual machine name
        :type name: str
        """
        super().__init__(simulation, name)
        self.cloud_compute_service_name = cloud_compute_service_name

    def start(self) -> BareMetalComputeService:
        """
        :return: A bare-metal compute service running on the VM
        :rtype: BareMetalComputeService
        """
        return self.simulation._start_vm(self.cloud_compute_service_name, self.name)

    def suspend(self) -> None:
        """
        Suspends a virtual machine.
        """
        return self.simulation._suspend_vm(self.cloud_compute_service_name, self.name)

    def resume(self) -> None:
        """
        Resumes a virtual machine.
        """
        return self.simulation._resume_vm(self.cloud_compute_service_name, self.name)

    def shutdown(self) -> None:
        """
        Shuts down a virtual machine.
        """
        return self.simulation._shutdown_vm(self.cloud_compute_service_name, self.name)

    def is_running(self) -> bool:
        """
        Determines whether a virtual machine is running.

        :return: True if the virtual machine is running, false otherwise
        :rtype: bool
        """
        return self.simulation._is_vm_running(self.cloud_compute_service_name, self.name)

    def is_suspended(self) -> bool:
        """
        Determines whether a virtual machine is suspended.

        :return: True if the virtual machine is suspended, false otherwise
        :rtype: bool
        """
        return self.simulation._is_vm_suspended(self.cloud_compute_service_name, self.name)

    def is_down(self) -> bool:
        """
        Determines whether a virtual machine is down.

        :return: True if the virtual machine is down, false otherwise
        :rtype: bool
        """
        return self.simulation._is_vm_down(self.cloud_compute_service_name, self.name)

    def __str__(self) -> str:
        """
        :return: String representation of a virtual machine
        :rtype: str
        """
        s = f"Virtual Machine {self.name} on Cloud Compute Service {self.cloud_compute_service_name}"
        return s

    def __repr__(self) -> str:
        """
        :return: String representation of a VirtualMachine object
        :rtype: str
        """
        s = f"VirtualMachine(name={self.name},cloud_compute_service={self.cloud_compute_service_name})"
        return s

