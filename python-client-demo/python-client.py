#!/usr/bin/env python3  
import sys
import requests
import json

class WRENCHException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
    pass

def waitForNextSimulationEvent():
    try:
        r = requests.get("http://localhost:8101/api/waitForNextSimulationEvent")
    except requests.exceptions.ConnectionError:
        sys.stderr.write("Cannot connect to WRENCH daemon... aborting\n")
        exit(1)

    response = r.json()
    return response


def submitStandardJob(job_name, cs_name):
    submission_spec = {"job_name": job_name, "service_name": cs_name}
    try:
        r = requests.post("http://localhost:8101/api/submitStandardJob", data=json.dumps(submission_spec))
    except requests.exceptions.ConnectionError:
        sys.stderr.write("Cannot connect to WRENCH daemon... aborting\n")
        exit(1)

    response = r.json()
    if (response["success"]):
        return
    else:
        raise WRENCHException(response["failure_cause"])

def getSimulationEvents():
    try:
        r = requests.get("http://localhost:8101/api/getSimulationEvents")
    except requests.exceptions.ConnectionError:
        sys.stderr.write("Cannot connect to WRENCH daemon... aborting\n")
        exit(1)

    print("R.TEXT = " + str(r.text))
    response = r.json()
    return response



def createStandardJob(task_name, task_flops, min_num_cores, max_num_cores):
    task_spec = {"task_name": task_name, "task_flops": task_flops, "min_num_cores": min_num_cores, "max_num_cores": max_num_cores}
    try:
        r = requests.post("http://localhost:8101/api/createStandardJob", data=json.dumps(task_spec))
    except requests.exceptions.ConnectionError:
        sys.stderr.write("Cannot connect to WRENCH daemon... aborting\n")
        exit(1)

    response = r.json()
    print(response)
    if (response["success"]):
        return response["job_id"]
    else:
        raise WRENCHException(response["failure_cause"])



def addTime(seconds):
    time_spec = {"increment": seconds}
    try:
        r = requests.post("http://localhost:8101/api/addTime", data=json.dumps(time_spec))
    except requests.exceptions.ConnectionError:
        sys.stderr.write("Cannot connect to WRENCH daemon... aborting\n")
        exit(1)
    return


def getSimulatedTime():

    try:
        r = requests.get("http://localhost:8101/api/getTime")
    except requests.exceptions.ConnectionError:
        sys.stderr.write("Cannot connect to WRENCH daemon... aborting\n")
        exit(1)

    response = r.json()

    return response["time"]



def createBareMetalComputeService(hostname):
    service_spec = {"service_type": "compute_baremetal", "head_host": hostname}
    try:
        r = requests.post("http://localhost:8101/api/addService", data=json.dumps(service_spec))
    except requests.exceptions.ConnectionError:
        sys.stderr.write("Cannot connect to WRENCH daemon... aborting\n")
        exit(1)

    response = r.json()

    if (response["success"]):
        return response["service_name"]
    else:
        raise WRENCHException(response["failure_cause"])

def getAllHostnames():
    try:
        r = requests.get("http://localhost:8101/api/getAllHostnames")
    except requests.exceptions.ConnectionError:
        sys.stderr.write("Cannot connect to WRENCH daemon... aborting\n")
        exit(1)

    response = r.json()

    return response["hostnames"]




if __name__ == "__main__":

    print("Time is " + str(getSimulatedTime()))
   
    print("Getting the names of all hosts in the platform...")
    hosts = getAllHostnames()
    print("Got the following hostnames: " + str(hosts))

    print("Creating a bare-metal compute service on ComputeHost...")
    cs_name = createBareMetalComputeService("ComputeHost")
    print("Created service has name " + cs_name)

    print("Sleeping for 10 seconds...")
    addTime(10)
    print("Done sleeping")

    print("Time is " + str(getSimulatedTime()))
   

    print("Creating a standard job...")
    job_name = createStandardJob("some_task", 100.0, 1, 1)
    print("Created standard job has name " + job_name)
    
    print("Submitting the standard job to the compute service...")
    submitStandardJob(job_name, cs_name)
    print("Job submitted")
    
    print("Sleeping for 1000 seconds...")
    addTime(1000)
    print("Done sleeping")

    print("Time is " + str(getSimulatedTime()))
   

    print("Getting simulation events...")
    events = getSimulationEvents()
    for event in events["event_queue"]:
        print("EVENT: " + str(event))
   
       
    print("Creating another standard job...")
    job_name = createStandardJob("some_other_task", 100.0, 1, 1)
    print("Created standard job has name " + job_name)
    
    print("Submitting the standard job to the compute service...")
    submitStandardJob(job_name, cs_name)
    print("Job submitted")

    print("Waiting for the next simulation event...")
    event = waitForNextSimulationEvent()
    print("Got this event: " + str(event))

    print("Time is " + str(getSimulatedTime()))
   
 
