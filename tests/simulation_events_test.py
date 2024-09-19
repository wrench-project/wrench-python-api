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
import sys

import wrench

if __name__ == "__main__":

    current_dir = pathlib.Path(__file__).parent.resolve()
    platform_file_path = pathlib.Path(current_dir / "sample_platform.xml")

    simulation = wrench.Simulation()

    try:
        simulation.start(platform_file_path, "ControllerHost")
    except wrench.WRENCHException as e:
        sys.stderr.write(f"Error: {e}\n")
        exit(1)

    cs = simulation.create_bare_metal_compute_service(
        "BatchHeadHost",
        {"BatchHost1": (6, 10.0),
         "BatchHost2": (6, 12.0)},
        "/scratch",
        {"BareMetalComputeServiceProperty::THREAD_STARTUP_OVERHEAD": "12s"},
        {"ServiceMessagePayload::STOP_DAEMON_MESSAGE_PAYLOAD": 1024.0})

    workflow = simulation.create_workflow()

    task1 = workflow.add_task("task1", 10, 1, 1, 0)
    job = simulation.create_standard_job([task1], {})

    cs.submit_standard_job(job)

    simulation.sleep(100)

    events = simulation.get_events()

    assert len(events) == 1, "There should be a single simulation event (instead there are " + str(len(events)) + ")"
    assert events[0]["event_type"] == "standard_job_completion", "Event type is unexpected"

    simulation.terminate()
