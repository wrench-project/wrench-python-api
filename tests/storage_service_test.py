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
import json
import sys

import wrench

if __name__ == "__main__":

    current_dir = pathlib.Path(__file__).parent.resolve()
    platform_file_path = pathlib.Path(current_dir / "sample_platform.xml")
    json_workflow_file_path = pathlib.Path(current_dir / "sample_wfcommons_workflow.json")

    simulation = wrench.Simulation()

    simulation.start(platform_file_path, "ControllerHost")

    ss = simulation.create_simple_storage_service("StorageHost", ["/"])
    # Coverage
    ss.get_name()
    str(ss)
    repr(ss)

    file1 = simulation.add_file("file1", 1024)
    ss.create_file_copy(file1)

    file2 = simulation.add_file("file2", 100000000)
    try:
        ss.create_file_copy(file2)
        raise wrench.WRENCHException("Shouldn't be able to store big file on storage service")
    except wrench.WRENCHException as e:
        pass

    ss.lookup_file(file1)
    ss.lookup_file(file2)

    try:
        file2._name = "BOGUS"  # Really horrible
        ss.lookup_file(file2)
        raise wrench.WRENCHException("Shouldn't be able to lookup bogus file")
    except wrench.WRENCHException as e:
        pass





