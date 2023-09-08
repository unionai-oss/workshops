"""A simple Flyte example."""

import typing
from flytekit import task, workflow, PodTemplate
from time import time
import requests
from kubernetes.client import V1PodSpec, V1Container, V1ResourceRequirements

modify_url = "http://localhost:8000/"
terminate_url = "http://localhost:8000/terminate"

pod = PodTemplate(
    primary_container_name="client",
    pod_spec=V1PodSpec(
        containers=[
            V1Container(
                name="client",
            ),
            V1Container(
                name="server",
                image="ghcr.io/zeryx/flytekit:podspec-server-4",
                command=["python", "server.py"],
                resources=V1ResourceRequirements(limits={"cpu": "2", "memory": "2Gi"},
                                                 requests={"cpu": "2", "memory": "2Gi"}),
                ports=[{"containerPort": 8000}],
            )
        ],
    )
)

@task(pod_template=pod, container_image="ghcr.io/zeryx/flytekit:podspec-client-latest")
def call_server(name: str) -> dict:
    t0 = time()
    response = requests.post(modify_url, json={"name": name})
    t1 = time()
    requests.delete(terminate_url)
    return {
        "time to call server": f"{(t1 - t0)*1000} ms",
        "time from server": response.json()["timestamp"],
        "name from server": response.json()["name"]
    }


@workflow
def client_server_wf(name: str = "union") -> dict:
    response = call_server(name=name)
    return response
