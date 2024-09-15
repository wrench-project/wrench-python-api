# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 The WRENCH Team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

import json

from wrench.compound_job import CompoundJob
from wrench.compute_service import ComputeService
from wrench.standard_job import StandardJob


# noinspection GrazieInspection
class BatchComputeService(ComputeService):
    """
    WRENCH Batch Compute Service class
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

    def submit_standard_job(self, standard_job: StandardJob, service_specific_args: dict[str, str]) -> None:
        """
        Submit a standard job to a batch compute service

        :param standard_job: the standard job
        :type standard_job: StandardJob
        :param service_specific_args: the service-specific arguments
        :type service_specific_args: dict[str, str]
        """
        return self._simulation._submit_standard_job(standard_job, self, json.dumps(service_specific_args))

    def submit_compound_job(self, compound_job: CompoundJob, service_specific_args: dict[str, str]) -> None:
        """
        Submit a compound job to a batch compute service

        :param compound_job: the compound job
        :type compound_job: CompoundJob
        :param service_specific_args: the service-specific arguments
        :type service_specific_args: dict[str, str]
        """
        return self._simulation._submit_compound_job(compound_job, self, json.dumps(service_specific_args))
