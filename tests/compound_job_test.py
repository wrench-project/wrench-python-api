import pathlib
import sys
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

        # Creating a  compute services
        bmcs = simulation.create_bare_metal_compute_service(
            "BatchHeadHost",
            {"BatchHost1": (6, 10.0),
             "BatchHost2": (6, 12.0)},
            "/scratch",
            {"BareMetalComputeServiceProperty::THREAD_STARTUP_OVERHEAD": "12s"},
            {"ServiceMessagePayload::STOP_DAEMON_MESSAGE_PAYLOAD": 1024.0})

        # Create two storage service
        ss1 = simulation.create_simple_storage_service("StorageHost", ["/"])
        ss2 = simulation.create_simple_storage_service("ControllerHost", ["/"])

        # Creating files
        file1 = simulation.add_file("file1", 1024)
        file2 = simulation.add_file("file2", 1024)

        # Adding a file to a storage service
        ss1.create_file_copy(file1)

        # Creating a compound job
        cj = simulation.create_compound_job("")
        print(f"Created compound job with name {cj.get_name()}")

        # Add a file write action to compound job
        fwa = cj.add_file_write_action("FileWriteAction1", file1, ss1)
        print(f"Adding {fwa.get_name()} to {cj.get_name()}")

        print(f"File Write Action get_file = {fwa.get_file()}")
        print(f"File Write Action get_file_location = {fwa.get_file_location()}")
        print(f"File Write Action uses_scratch = {fwa.uses_scratch}")

        # Add a file read action to compound job
        fra = cj.add_file_read_action("FileReadAction1", file1, ss1)
        print(f"Adding {fra.get_name()} to {cj.get_name()}")

        print(f"File Read Action get_file = {fra.get_file()}")
        print(f"File Read Action get_file_location = {fra.get_file_location()}")
        print(f"File Read Action get_num_bytes_to_read = {fra.get_file_location()}")
        print(f"File Read Action uses_scratch = {fra.uses_scratch}")

        # Add a file copy action to compound job
        fca = cj.add_file_copy_action("FileCopyAction1", file1, ss1, ss2)
        print(f"Adding {fca.get_name()} to {cj.get_name()}")

        print(f"File Copy Action getFile = {fca.get_file()}")
        print(f"File Copy Action getSourceFileLocation = {fca.get_source_file_location()}")
        print(f"File Copy Action getDestinationFileLocation = {fca.get_destination_file_location()}")
        print(f"File Copy Action usesScratch = {fca.uses_scratch}")

        # Add a file delete action to compound job
        fda = cj.add_file_delete_action("FileDeleteAction1", file1, ss1)
        print(f"Adding {fda.get_name()} to {cj.get_name()}")

        print(f"File Delete Action getFile = {fda.get_file()}")
        print(f"File Delete Action getFileLocation = {fda.get_file_location()}")
        print(f"File Delete Action usesScratch = {fda.uses_scratch}")

        # Add a sleep action to compound job
        sa = cj.add_sleep_action("SleepAction1", 5.0)
        print(f"Adding {sa.get_name()} to {cj.get_name()}")

        print(f"Sleep Action getSleepTime = {sa.get_sleep_time()}")

        # Add a compute action to compound job
        ca = cj.add_compute_action("ComputeAction1", 100.0, 0.0, 2, 1, ("AMDAHL", 0.8))
        print(f"Adding {ca.get_name()} to {cj.get_name()}")

        print(f"Compute Action getFlops = {ca.get_flops()}")
        print(f"Compute Action getMaxNumCores = {ca.get_max_num_cores()}")
        print(f"Compute Action getMinNumCores = {ca.get_min_num_cores()}")
        print(f"Compute Action getMinRAMFootprint = {ca.get_min_ram_footprint()}")
        print(f"Compute Action getParallelModel = {ca.get_parallel_model()}")

        # # Add a parent compound job to another compound job
        cj2_0 = simulation.create_compound_job("")
        print(f"Created compound job with name {cj2_0.get_name()}")
        cj2_0.add_sleep_action("SleepAction2", 2.0)

        cj2_1 = simulation.create_compound_job("")
        print(f"Created compound job with name {cj2_1.get_name()}")
        cj2_1.add_sleep_action("SleepAction3", 2.0)

        print("Adding parent compound job")
        cj2_1.add_parent_job(cj2_0)

        print(f"Time before submitting compound jobs 2/3 is {simulation.get_simulated_time()}")

        print("Submitting the parent compound job to the base metal compute service...")
        bmcs.submit_compound_job(cj2_0)

        print(f"Time after submitting compound jobs 2/3 is {simulation.get_simulated_time()}")

        # Get the actions of compound job
        print(f"Compound Job's get_actions = {cj.get_actions()}")

        print("Submitting the compound job to the base metal compute service...")
        bmcs.submit_compound_job(cj)

        print("Synchronously waiting for the next simulation event...")
        event = simulation.wait_for_next_event()
        print(f"  - Event: {event}")
        print(f"Time is {simulation.get_simulated_time()}")

        print("Synchronously waiting for the next simulation event...")
        event = simulation.wait_for_next_event()
        print(f"  - Event: {event}")
        print(f"Time is {simulation.get_simulated_time()}")

        print("Get the start/end date of the compute action...")
        print(f"Compute action start date: {ca.get_start_date()}")
        print(f"Compute action end date: {ca.get_end_date()}")

        print("Terminating simulation")
        simulation.terminate()

    except wrench.WRENCHException as e:
        sys.stderr.write(f"Error: {e}\n")
        exit(1)
