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


class StandardJob(SimulationItem):
    """
    WRENCH Standard Job class
    """

    def get_tasks(self):
        return self.simulation.standard_job_get_tasks(self.name)
