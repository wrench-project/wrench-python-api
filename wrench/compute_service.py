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


class ComputeService(SimulationItem):
    """
    WRENCH Compute Service class
    :param simulation: simulation object
    :type simulation
    :param name: Compute service name
    :type name: str
    """

    def __init__(self, simulation, name: str) -> None:
        """
        Constructor
        """
        super().__init__(simulation, name)

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

    def __str__(self) -> str:
        """
        :return: String representation of a compute service
        :rtype: str
        """
        s = f"Compute Service {self.name}"
        return s

    def __repr__(self) -> str:
        """
        :return: String representation of a ComputeService object
        :rtype: str
        """
        s = f"ComputeService(name={self.name})"
        return s

