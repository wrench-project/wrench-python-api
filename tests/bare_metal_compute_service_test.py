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

    if len(sys.argv) != 2:
        sys.stderr.write(f"Usage: {sys.argv[0]} <# seconds of real time to sleep during simulation>\n")
        exit(1)

    try:
        current_dir = pathlib.Path(__file__).parent.resolve()
        platform_file_path = pathlib.Path(current_dir / "sample_platform.xml")

        simulation = wrench.Simulation()
        simulation.start(platform_file_path, "ControllerHost")

        time.sleep(5)
        cs = simulation.create_bare_metal_compute_service(
            "BatchHeadNode",
            {"Host1": (6, 10.0),
             "Host2": (6, 12.0)},
            "/scratch",
            {"BareMetalComputeServiceProperty::THREAD_STARTUP_OVERHEAD": "12s"},
            {"ServiceMessagePayload::STOP_DAEMON_MESSAGE_PAYLOAD": 1024.0})

        print(f"Created compute service has name {cs.get_name()}")

        print(f"Compute service supported jobs")

        print(f"Compound Jobs: {cs.supportsCompoundJobs()}\n"
              f"Pilot Jobs: {cs.supportsPilotJobs()}\n"
              f"Standard Jobs: {cs.supportsStandardJobs}")

        print(f"Time is {simulation.get_simulated_time()}")

        # ToDo: In wrench daemon, the route starts with /api, anything to change?
        print("Terminating simulation daemon")
        simulation.terminate()

    except wrench.WRENCHException as e:
        print(f"Error: {e}")
        exit(1)
