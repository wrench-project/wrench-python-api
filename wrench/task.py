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


class Task(SimulationItem):
    """
    WRENCH Task class
    """

    def get_flops(self):
        return self.simulation.task_get_flops(self.name)

    def get_min_num_cores(self):
        return self.simulation.task_get_min_num_cores(self.name)

    def get_max_num_cores(self):
        return self.simulation.task_get_max_num_cores(self.name)

    def get_memory(self):
        return self.simulation.task_get_memory(self.name)
