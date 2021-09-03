import requests
import json


class WRENCHException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    pass


def kill_daemon():
    try:
        requests.post("http://localhost:8101/api/stop")
    except requests.exceptions.ConnectionError:
        pass
    return


def wait_for_next_event():
    try:
        r = requests.get("http://localhost:8101/api/waitForNextSimulationEvent")
    except requests.exceptions.ConnectionError:
        raise WRENCHException("Cannot connect to WRENCH daemon")

    response = r.json()
    return response["event"]


def submit_standard_job(job_name, cs_name):
    submission_spec = {"job_name": job_name, "service_name": cs_name}
    try:
        r = requests.post("http://localhost:8101/api/submitStandardJob", data=json.dumps(submission_spec))
    except requests.exceptions.ConnectionError:
        raise WRENCHException("Cannot connect to WRENCH daemon")

    response = r.json()
    if response["success"]:
        return
    else:
        raise WRENCHException(response["failure_cause"])


def get_simulation_events():
    try:
        r = requests.get("http://localhost:8101/api/getSimulationEvents")
    except requests.exceptions.ConnectionError:
        raise WRENCHException("Cannot connect to WRENCH daemon")

    response = r.json()["events"]
    return response


def create_standard_job(task_name, task_flops, min_num_cores, max_num_cores):
    task_spec = {"task_name": task_name, "task_flops": task_flops, "min_num_cores": min_num_cores,
                 "max_num_cores": max_num_cores}
    try:
        r = requests.post("http://localhost:8101/api/createStandardJob", data=json.dumps(task_spec))
    except requests.exceptions.ConnectionError:
        raise WRENCHException("Cannot connect to WRENCH daemon")

    response = r.json()
    print(response)
    if response["success"]:
        return response["job_id"]
    else:
        raise WRENCHException(response["failure_cause"])


def sleep(seconds):
    time_spec = {"increment": seconds}
    try:
        requests.post("http://localhost:8101/api/addTime", data=json.dumps(time_spec))
    except requests.exceptions.ConnectionError:
        raise WRENCHException("Cannot connect to WRENCH daemon")

    return


def get_simulated_time():
    try:
        r = requests.get("http://localhost:8101/api/getTime")
    except requests.exceptions.ConnectionError:
        raise WRENCHException("Cannot connect to WRENCH daemon")

    response = r.json()
    return response["time"]


def create_bare_metal_compute_service(hostname):
    service_spec = {"service_type": "compute_baremetal", "head_host": hostname}
    try:
        r = requests.post("http://localhost:8101/api/addService", data=json.dumps(service_spec))
    except requests.exceptions.ConnectionError:
        raise WRENCHException("Cannot connect to WRENCH daemon")

    response = r.json()

    if response["success"]:
        return response["service_name"]
    else:
        raise WRENCHException(response["failure_cause"])


def get_all_hostnames():
    try:
        r = requests.get("http://localhost:8101/api/getAllHostnames")
    except requests.exceptions.ConnectionError:
        raise WRENCHException("Cannot connect to WRENCH daemon")

    response = r.json()

    return response["hostnames"]
