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
        cs = simulation.create_bare_metal_compute_service("ComputeHost")

        print("Created service has name " + cs.get_name())

        print("Sleeping for 10 seconds...")
        simulation.sleep(10)
        print("Time now is " + str(simulation.get_simulated_time()))

        print("Creating a task")
        task1 = simulation.create_task("task1", 100.0, 1, 1, 0)
        print("Just created a task with flops=" + str(task1.get_flops()) +
              ", min_num_cores=" + str(task1.get_min_num_cores()) +
              ", max_num_cores=" + str(task1.get_max_num_cores()) +
              ", memory=" + str(task1.get_memory()))

        print("Creating a standard job with a single 100.0 flop task")
        job = simulation.create_standard_job([task1])

        print("Created standard job has name " + job.get_name())

        print("Submitting the standard job to the compute service...")
        cs.submit_standard_job(job)
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
        print("Sleeping " + sys.argv[1] + " seconds in real time")
        os.system("sleep " + sys.argv[1])

        print("Creating another task")
        task2 = simulation.create_task("task2", 100.0, 1, 1, 0)


        print("Creating another job...")
        other_job = simulation.create_standard_job([task2])
        print("Created standard job has name " + other_job.get_name())

        print("Submitting the standard job to the compute service...")
        cs.submit_standard_job(other_job)
        print("Job submitted!")

        print("Synchronously waiting for the next simulation event...")
        event = simulation.wait_for_next_event()
        print("  - Event: " + str(event))

        print("That Job's tasks are:")
        tasks = event["job"].get_tasks()
        for t in tasks:
            print("  - " + t.get_name())

        print("Time is " + str(simulation.get_simulated_time()))

        print("Terminating simulation daemon")
        simulation.terminate()

    except WRENCHException as e:
        print("Error: " + str(e))
        exit(1)

