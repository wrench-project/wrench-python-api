# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 The WRENCH Team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
from wrench.action import Action
from wrench.compound_job import CompoundJob


class ComputeAction(Action):
    """
    WRENCH Action class
    """
    def __init__(self, simulation, compound_job: CompoundJob, name: str, flops: float, ram: float, min_num_cores: int,
                 max_num_cores: int, parallel_model: tuple) -> None:

        """
        Constructor

        :param simulation: simulation object
        :type simulation
        :param compound_job: compound job object
        :type compound_job: CompoundJob
        :param name: name of compute action
        :type name: str
        :param flops: amount of flops this action has
        :type flops: float
        :param ram: minimum amount of ram this action needs
        :type ram: float
        :param min_num_cores: minimum amount of cores this action needs
        :type min_num_cores: int
        :param max_num_cores: maximum amount of cores this action can use
        :type max_num_cores: int
        :param parallel_model: type of parallel model and settings for it
        :type parallel_model: tuple
        """
        self.flops = flops
        self.ram = ram
        self.min_num_cores = min_num_cores
        self.max_num_cores = max_num_cores
        self.parallel_model = parallel_model
        super().__init__(simulation, name, compound_job)

    def get_flops(self) -> float:
        """
        Get flops

        :return: flops
        :rtype: float
        """
        return self.flops

    def get_max_num_cores(self) -> int:
        """
        Get this actions maximum amount of cores

        :return: Maximum amount of cores
        :rtype: long
        """
        return self.max_num_cores

    def get_min_num_cores(self) -> int:
        """
        Get this actions minimum amount of cores

        :return: Minimum amount of cores
        :rtype: long
        """
        return self.min_num_cores

    def get_min_ram_footprint(self) -> float:
        """
        Minimum amount of ram needed for this action

        :return: Minimum amount of ram needed
        :rtype: float
        """
        return self.ram

    def get_parallel_model(self) -> tuple:
        """
        Returns type of parallel model and settings for it

        :return: the type of parallel model and a number that determines its configuration
        :rtype: tuple[str, float]
        """
        return self.parallel_model

    def __str__(self) -> str:
        """
        :return: String representation of the sleep action
        :rtype: str
        """
        s = f"Sleep Action {self.name}"
        return s

    def __repr__(self) -> str:
        """
        :return: String representation of the sleep action object
        :rtype: str
        """
        s = f"SleepAction(name={self.name})"
        return s
