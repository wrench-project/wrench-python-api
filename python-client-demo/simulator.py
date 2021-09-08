#!/usr/bin/env python3  
from pywrench import pywrench
from pywrench.exception import WRENCHException
import sys

if __name__ == "__main__":

    if len(sys.argv) != 2:
        sys.stderr.write("Usage: " + sys.argv[0] + " <# seconds of real time to sleep during simulation>\n");
        exit(1)

    try:
        simulation = pywrench.start_simulation("./three_host_platform.xml", "ControllerHost")

        print("New simulation, time is " + str(simulation.get_simulated_time()))

        hosts = simulation.get_all_hostnames()
        print("Hosts in the platform are: " + str(hosts))

        print("Creating a bare-metal compute service on ComputeHost...")
        cs_name = simulation.create_bare_metal_compute_service("ComputeHost")
        print("Created service has name " + cs_name)

        print("Sleeping for 10 seconds...")
        simulation.sleep(10)

        print("Time now is " + str(simulation.get_simulated_time()))

        print("Creating a standard job with a single 100.0 flop task")
        job_name = simulation.create_standard_job("some_task", 100.0, 1, 1)
        print("Created standard job has name " + job_name)

        print("Submitting the standard job to the compute service...")
        simulation.submit_standard_job(job_name, cs_name)
        print("Job submitted!")

        print("Sleeping for 1000 seconds...")
        simulation.sleep(1000)

        print("Time now is " + str(simulation.get_simulated_time()))

        print("Getting simulation events that have occurred while I slept...")
        events = simulation.get_simulation_events()
        for event in events:
            print("  - Event: " + str(event))

        import os
        import sys
        os.system("sleep " + sys.argv[1])

        print("Creating another standard job...")
        job_name = simulation.create_standard_job("some_other_task", 100.0, 1, 1)
        print("Created standard job has name " + job_name)

        print("Submitting the standard job to the compute service...")
        simulation.submit_standard_job(job_name, cs_name)
        print("Job submitted!")

        print("Synchronously waiting for the next simulation event...")
        event = simulation.wait_for_next_event()
        print("  - Event: " + str(event))

        print("Time is " + str(simulation.get_simulated_time()))

        print("Terminating simulation daemon")
        simulation.terminate()

    except WRENCHException as e:
        print("Error: " + str(e))
        exit(1)

