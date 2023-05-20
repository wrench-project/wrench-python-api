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
        return self.simulation.supports_compound_jobs()

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


