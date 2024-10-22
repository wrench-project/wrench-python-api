#!/usr/bin/env python3
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

    with open(platform_file_path, "r") as platform_file:
        xml_string = platform_file.read()
    try:
        simulation.start(xml_string, "ControllerHost")
    except wrench.WRENCHException as e:
        sys.stderr.write(f"Error: {e}\n")
        exit(1)

    assert simulation.get_simulated_time() == 0, "The simulation time should be zero"

    ss1 = simulation.create_simple_storage_service("ControllerHost", ["/"])
    ss2 = simulation.create_simple_storage_service("StorageHost", ["/"])

    try:
        bogus_frs = simulation.create_file_registry_service("ControllerHost_BOGUS")
    except wrench.WRENCHException as e:
        pass
    frs = simulation.create_file_registry_service("ControllerHost")
    # Coverage
    frs.get_name()
    str(frs)
    repr(frs)

    file1 = simulation.add_file("file1", 1024)
    file2 = simulation.add_file("file2", 1024)
    file3 = simulation.add_file("file3", 1024)

    frs.add_entry(ss1, file1)
    assert frs.lookup_entry(file1) == [ss1], "Should find file1 entry in file registry service"
    frs.add_entry(ss2, file1)
    assert ss1 in frs.lookup_entry(file1) and ss2 in frs.lookup_entry(file1), "Should find file1 entry in file registry service"

    assert frs.lookup_entry(file2) == [], "Should not find file2 entry in file registry service"

    frs.remove_entry(ss1, file1)
    assert frs.lookup_entry(file1) == [ss2], "Should not find entry in file registry service"

    frs.remove_entry(ss2, file1)
    assert frs.lookup_entry(file1) == [], "Should not find entry in file registry service"


    simulation.terminate()
