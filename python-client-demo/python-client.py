#!/usr/bin/env python3  
import requests
import json

service_spec = {"service_type": "compute_baremetal", "head_host": "BatchHeadNode"}
r = requests.post("http://localhost:8101/api/addService", data=json.dumps(service_spec))
print(r.text)


