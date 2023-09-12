# Client - Server communication using a Flyte Task

This example showcases how to create both a client and server container within a Flyte Task Pod.

It leverages the [PodTemplate](https://docs.flyte.org/en/latest/deployment/configuration/general.html#using-k8s-podtemplates) system to create a pod with two containers, one for the client and one for the server.

## Features 
- ContainerTasks
- PodTemplates
- Fixed container_image paths
- multi-container pods

## Running the example
No additional setup is required to run this example. Simply run the following command from the root of the repository:

```bash
pyflyte register workflows/client_server.py --project flytesnacks --domain development
```