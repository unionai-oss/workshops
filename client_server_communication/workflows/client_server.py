"""A simple Flyte example."""

import typing
from flytekit import task, workflow, PodTemplate
from time import time
import requests
from kubernetes.client import V1PodSpec, V1Container, V1ResourceRequirements

localhost_path = "http://localhost:8000"

interact_url = f"{localhost_path}/"
terminate_url = f"{localhost_path}/terminate"

# Replace these ghcr image paths with your own image registry
client_img = "ghcr.io/unionai-oss/workshops:w2-client-latest"
server_img = "ghcr.io/unionai-oss/workshops:w2-server-latest"

# This is the pod spec that will be used to run the server
# Note that the server is running on port 8000, and is only accessible from within the pod
# The server is also terminated by sending a DELETE request to /terminate

pod = PodTemplate(
    primary_container_name="client",
    pod_spec=V1PodSpec(
        containers=[
            V1Container(
                name="client",
            ),
            V1Container(
                name="server",
                image=server_img,
                command=["python", "server.py"],
                resources=V1ResourceRequirements(limits={"cpu": "2", "memory": "2Gi"},
                                                 requests={"cpu": "2", "memory": "2Gi"}),
                ports=[{"containerPort": 8000}],
            )
        ],
    )
)


#
@task(pod_template=pod, container_image=client_img)
def client_function(name: str) -> dict:
    try:
        t0 = time()
        response = requests.post(interact_url, json={"name": name})
        t1 = time()
        output = {
            "time to call server": f"{(t1 - t0) * 1000} ms",
            "time from server": response.json()["timestamp"],
            "name from server": response.json()["name"]
        }
        return output
    finally:
        requests.delete(terminate_url)


@workflow
def client_server_wf(name: str = "union") -> dict:
    return client_function(name=name)
