# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 The WRENCH Team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
from wrench.compute_service import ComputeService


# noinspection GrazieInspection
class BareMetalComputeService(ComputeService):
    """
    WRENCH Bare Metal Compute Service class
    """

    def __init__(self, simulation, name: str) -> None:
        """
        Constructor

        :param simulation: The simulation
        :type simulation
        :param name: Compute service name
        :type name: str
        """
        super().__init__(simulation, name)
