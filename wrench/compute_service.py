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


# noinspection GrazieInspection
class ComputeService(SimulationItem):
    """
    WRENCH Compute Service class
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

    def supports_compound_jobs(self) -> bool:
        """
        Determine whether the compute service supports compound jobs

        :return: True if compound jobs are supported, false otherwise
        :rtype: bool
        """
        return self.simulation._supports_compound_jobs(self)

    def supports_pilot_jobs(self) -> bool:
        """
        Determine whether the compute service supports pilot jobs

        :return: True if pilot jobs are supported, false otherwise
        :rtype: bool
        """
        return self.simulation._supports_pilot_jobs(self)

    def supports_standard_jobs(self) -> bool:
        """
        Determine whether the compute service supports standard jobs

        :return: True if standard jobs are supported, false otherwise
        :rtype: bool
        """
        return self.simulation._supports_standard_jobs(self)

    def __str__(self) -> str:
        """
        :return: String representation of the compute service

        :rtype: str
        """
        s = f"Compute Service {self.name}"
        return s

    def __repr__(self) -> str:
        """
        :return: String representation of the ComputeService object
        :rtype: str
        """
        s = f"ComputeService(name={self.name})"
        return s
