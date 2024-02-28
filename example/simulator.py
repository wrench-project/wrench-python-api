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
import wrench

if __name__ == "__main__":

    try:
        # Instantiating the simulation based on a platform description file
        current_dir = pathlib.Path(__file__).parent.resolve()
        platform_file_path = pathlib.Path(current_dir / "sample_platform.xml")

        # Creating a new WRENCH simulation
        simulation = wrench.Simulation()

        # Starting the simulation, with this simulated process running on the host ControllerHost
        simulation.start(platform_file_path, "ControllerHost")

        print(f"Simulation, time is {simulation.get_simulated_time()}")

        hosts = simulation.get_all_hostnames()
        print(f"Hosts in the platform are: {hosts}")

        # Creating a file registry service
        print("Creating a file registry service on ControllerHost...")
        frs = simulation.create_file_registry_service("ControllerHost")
        print(f"Created file registry service has name {frs.get_name()}")

        # Creating a storage service
        print("Creating a simple storage service on StorageHost...")
        ss = simulation.create_simple_storage_service("StorageHost", ["/"])
        print(f"Created storage service has name {ss.get_name()}")

        print("Creating a file registry service on ControllerHost...")
        frs = simulation.create_file_registry_service("ControllerHost")
        print(f"Created file registry service has name {frs.get_name()}")

        print("Adding a 1kB file to the simulation...")
        file1 = simulation.add_file("file1", 1024)
        print(f"Created file {file1}")

        print(f"Creating a copy of {file1} on the storage service")
        ss.create_file_copy(file1)

        # Add an entry to the file registry service
        print(f"Adding an entry for {file1} on the file registry service {frs.get_name()}")
        frs.add_entry(ss, file1)

        # Looking the entry
        ss_list = frs.lookup_entry(file1)
        print(f"Entries for file: {ss_list}")

        # Remove an entry to the file registry service
        print(f"Removing an entry for {file1} on the file registry service {frs.get_name()}")
        frs.remove_entry(ss, file1)

        # Looking the entry again (which should fail)
        ss_list = frs.lookup_entry(file1)
        print(f"Entries for file: {ss_list}")

        print(f"Time is {simulation.get_simulated_time()}")

        print("Terminating simulation daemon")
        simulation.terminate()

    except wrench.WRENCHException as e:
        print(f"Error: {e}")
        exit(1)
