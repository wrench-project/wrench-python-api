#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 The WRENCH Team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from abc import ABC


class SimulationItem(ABC):
    """
    WRENCH Simulation Item class

    :param simulation: simulation object
    :type simulation: WRENCHSimulation
    :param name: simulation item name
    :type name: str
    """

    def __init__(self, simulation, name: str) -> None:
        """
        Constructor
        """
        self.simulation = simulation
        self.name = name

    def get_name(self) -> str:
        """
        Get the simulation item name
        """
        return self.name
