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
    :type simulation: WRENCHSimulation
    :param name: Task name
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
