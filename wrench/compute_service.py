# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 The WRENCH Team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from wrench.simulation_item import SimulationItem
from typing import Dict

from wrench.compound_job import CompoundJob
from wrench.standard_job import StandardJob


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
        return self._simulation._supports_compound_jobs(self)

    def supports_pilot_jobs(self) -> bool:
        """
        Determine whether the compute service supports pilot jobs

        :return: True if pilot jobs are supported, false otherwise
        :rtype: bool
        """
        return self._simulation._supports_pilot_jobs(self)

    def supports_standard_jobs(self) -> bool:
        """
        Determine whether the compute service supports standard jobs

        :return: True if standard jobs are supported, false otherwise
        :rtype: bool
        """
        return self._simulation._supports_standard_jobs(self)

    def get_core_flop_rates(self) -> Dict[str, float]:
        """
        Get the map of core speeds, keyed by host name

        :return: A dictionary of core speeds
        :rtype: Dict[str, float]
        """
        return self._simulation._get_core_flop_rates(self)

    def get_core_counts(self) -> Dict[str, int]:
        """
        Get the map of core counts, keyed by host name

        :return: A dictionary of core counts
        :rtype: Dict[str, int]
        """
        return self._simulation._get_core_counts(self)

    def submit_standard_job(self, standard_job: StandardJob) -> None:
        """
        Submit a standard job to the compute service

        :param standard_job: the standard job
        :type standard_job: StandardJob
        """
        return self._simulation._submit_standard_job(standard_job, self)

    def submit_compound_job(self, compound_job: CompoundJob) -> None:
        """
        Submit a compound job to the compute service

        :param compound_job: the compound job
        :type compound_job: CompoundJob
        """
        return self._simulation._submit_compound_job(compound_job, self)

    def __str__(self) -> str:
        """
        :return: String representation of the compute service

        :rtype: str
        """
        s = f"Compute Service {self._name}"
        return s

    def __repr__(self) -> str:
        """
        :return: String representation of the ComputeService object
        :rtype: str
        """
        s = f"ComputeService(name={self._name})"
        return s
