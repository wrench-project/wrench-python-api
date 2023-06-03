#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 The WRENCH Team.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
import pathlib
import os
import sys
import time

import wrench

if __name__ == "__main__":

    try:
        current_dir = pathlib.Path(__file__).parent.resolve()
        platform_file_path = pathlib.Path(current_dir / "sample_platform.xml")

        simulation = wrench.Simulation()
        simulation.start(platform_file_path, "ControllerHost")

        print(f"New simulation, time is {simulation.get_simulated_time()}")
        hosts = simulation.get_all_hostnames()
        print(f"Hosts in the platform are: {hosts}")
        print(f"Creating compute resources")
        print("Creating a bare-metal compute service on ComputeHost...")

        cs = simulation.create_bare_metal_compute_service(
            "BatchHeadHost",
            {"BatchHost1": (6, 10.0),
             "BatchHost2": (6, 12.0)},
            "/scratch",
            {"BareMetalComputeServiceProperty::THREAD_STARTUP_OVERHEAD": "12s"},
            {"ServiceMessagePayload::STOP_DAEMON_MESSAGE_PAYLOAD": 1024.0})

        print(f"Created compute service has name {cs.get_name()}")

        print(f"Compute service supported jobs")
        print(f"Supports Compound Jobs: {cs.supports_compound_jobs()}\n"
               f"Supports Pilot Jobs: {cs.supports_pilot_jobs()}\n"
               f"Supports Standard Jobs: {cs.supports_standard_jobs()}")

        print(f"Time is {simulation.get_simulated_time()}")

        # ToDo: In wrench daemon, the route starts with /api, anything to change?
        print("Terminating simulation daemon")
        simulation.terminate()

    except wrench.WRENCHException as e:
        print(f"Error: {e}")
        exit(1)
