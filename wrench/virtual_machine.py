# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 The WRENCH Team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from wrench.bare_metal_compute_service import BareMetalComputeService
    from wrench.cloud_compute_service import CloudComputeService

from wrench.simulation_item import SimulationItem


# noinspection GrazieInspection
class VirtualMachine(SimulationItem):
    """
    WRENCH Virtual Machine class
    """

    def __init__(self, simulation, cloud_compute_service: CloudComputeService, name: str) -> None:
        """
        Constructor

        :param simulation: simulation object
        :type simulation
        :param cloud_compute_service: the cloud compute service
        :type cloud_compute_service: CloudComputeService
        :param name: VM name
        :type name: str
        """
        super().__init__(simulation, name)
        self.cloud_compute_service = cloud_compute_service

    def get_cloud_compute_service(self) -> CloudComputeService:
        """
        Get the cloud compute service on which the VM runs

        :return: a cloud compute service
        :rtype: CloudComputeService
        """
        return self.cloud_compute_service

    def start(self) -> BareMetalComputeService:
        """
        Start the VM

        :return: A bare-metal compute service running on the VM
        :rtype: BareMetalComputeService
        """
        return self._simulation._start_vm(self)

    def suspend(self) -> None:
        """
        Suspend the VM
        """
        return self._simulation._suspend_vm(self)

    def resume(self) -> None:
        """
        Resume the VM
        """
        return self._simulation._resume_vm(self)

    def shutdown(self) -> None:
        """
        Shutdown the VM
        """
        return self._simulation._shutdown_vm(self)

    def is_running(self) -> bool:
        """
        Determine whether the VM is running

        :return: True if the VM is running, false otherwise
        :rtype: bool
        """
        return self._simulation._is_vm_running(self)

    def is_suspended(self) -> bool:
        """
        Determine whether the VM is suspended

        :return: True if the VM is suspended, false otherwise
        :rtype: bool
        """
        return self._simulation._is_vm_suspended(self)

    def is_down(self) -> bool:
        """
        Determine whether the VM is down

        :return: True if the VM is down, false otherwise
        :rtype: bool
        """
        return self._simulation._is_vm_down(self)

    def __str__(self) -> str:
        """
        :return: String representation of the VM
        :rtype: str
        """
        s = f"Virtual Machine {self._name} on Cloud Compute Service {self.get_cloud_compute_service().get_name()}"
        return s

    def __repr__(self) -> str:
        """
        :return: String representation of the VirtualMachine object
        :rtype: str
        """
        s = f"VirtualMachine(name={self._name},cloud_compute_service={self.get_cloud_compute_service().get_name()})"
        return s
