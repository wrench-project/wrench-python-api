# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 The WRENCH Team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.


# noinspection GrazieInspection
class SimulationItem:
    """
    WRENCH Simulation Item class
    """

    def __init__(self, simulation, name: str) -> None:
        """
        Constructor

        :param simulation: simulation object
        :type simulation
        :param name: simulation item name
        :type name: str
        """
        self.simulation = simulation
        self.name = name

    def get_name(self) -> str:
        """
        Get the name
        """
        return self.name
