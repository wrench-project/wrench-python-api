#!/usr/bin/env python3  
import sys
import requests
import json

class WRENCHException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
    pass


def addTime(seconds):
    time_spec = {"increment": seconds}
    try:
        r = requests.post("http://localhost:8101/api/addTime", data=json.dumps(time_spec))
    except requests.exceptions.ConnectionError:
        sys.stderr.write("Cannot connect to WRENCH daemon... aborting\n");
        exit(1)
    return


def getSimulatedTime():

    try:
        r = requests.get("http://localhost:8101/api/getTime")
    except requests.exceptions.ConnectionError:
        sys.stderr.write("Cannot connect to WRENCH daemon... aborting\n");
        exit(1)

    response = r.json()

    return response["time"]



def createBareMetalComputeService(hostname):
    service_spec = {"service_type": "compute_baremetal", "head_host": hostname}
    try:
        r = requests.post("http://localhost:8101/api/addService", data=json.dumps(service_spec))
    except requests.exceptions.ConnectionError:
        sys.stderr.write("Cannot connect to WRENCH daemon... aborting\n");
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
        sys.stderr.write("Cannot connect to WRENCH daemon... aborting\n");
        exit(1)

    response = r.json()

    return response["hostnames"]




if __name__ == "__main__":

    print("Asking what time it is...")
    date = getSimulatedTime()
    print("Was told that time is " + str(date))
   
    print("Getting the names of all hosts in the platform...")
    hosts = getAllHostnames()
    print("Got the following hostnames: " + str(hosts))

    print("Creating a bare-metal compute service on ComputeHost...")
    cs_name = createBareMetalComputeService("ComputeHost")
    print("Created service has name " + cs_name)

    print("Sleeping for 10 seconds...")
    addTime(10)
    print("Done sleeping")

    print("Asking what time it is...")
    date = getSimulatedTime()
    print("Was told that time is " + str(date))
   

    
   
   
   

