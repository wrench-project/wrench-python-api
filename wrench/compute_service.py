#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 The WRENCH Team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

import json

from .simulation_item import SimulationItem


class ComputeService(SimulationItem):
    """
    WRENCH Compute Service class
    """

    def submit_standard_job(self, standard_job):
        return self.simulation.submit_standard_job(standard_job.get_name(), self.name)
