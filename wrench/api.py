#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 The WRENCH Team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from .simulation import WRENCHSimulation
from .exception import WRENCHException


def start_simulation(platform_file_path, controller_hostname, daemon_host="localhost", daemon_port=8101):
    """
    Start a new simulation

    :param platform_file_path: path of a file that contains the simulated platform's description in XML
    :param controller_hostname: the name of the (simulated) host in the platform on which the simulation concroller will run
    :param daemon_host: the name of the host on which the WRENCH daemon is running
    :param daemon_port: port number on which the WRENCH daemon is listening

    :return:
    """
    try:
        return WRENCHSimulation(platform_file_path, controller_hostname, daemon_host, daemon_port)
    except WRENCHException:
        raise
