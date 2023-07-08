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


class BareMetalComputeService(ComputeService):
    """
    WRENCH Bare Metal Compute Service class
    :param compute_service: Compute Service
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

    def __str__(self) -> str:
        """
        :return: String representation of a bare metal compute service
        :rtype: str
        """
        s = f"Compute Service {self.name}"
        return s

    def __repr__(self) -> str:
        """
        :return: String representation of a BareMetalComputeService object
        :rtype: str
        """
        s = f"ComputeService(name={self.name})"
        return s

