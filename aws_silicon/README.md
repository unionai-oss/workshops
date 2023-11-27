# Flyte x AWS Accelerators

This project leverages the AWS Silicon Accelerators (Inferentia and Trainium) to accelerate a simple Resnet50 model.
The primary showcase is the possibility and performance characteristics of Inferentia and Trainium on Flyte.
## Usage

To get up and running, you will need an EKS Flyte cluster with Neuronx based accelerator nodes enabled and configured correctly.

### Setup

#### inf2 nodegroup configuration
Create a new nodegroup in an existing Flyte EKS cluster with the following configuration:
```yaml
  - type: aws-nodegroup
    min_nodes: 0
    max_nodes: 2
    node_disk_size: 500
    node_instance_type: inf2.8xlarge
    ami_type: AL2_x86_64_GPU
    name: inf28xlarge
    iam_role_arn: ${{module.flyteworker.nodegroup_role_arn}}
    labels:
      flyte.org/node-role: worker
      k8s.amazonaws.com/accelerator: aws-inferentia2
    taints:
      - key: flyte.org/node-role
        value: worker
        effect: "NO_SCHEDULE"
    autoscaling_tags:
      k8s.io/cluster-autoscaler/node-template/label/eks.amazonaws.com/capacityType: ON_DEMAND
      k8s.io/cluster-autoscaler/node-template/label/flyte.org/node-role: worker
      k8s.io/cluster-autoscaler/node-template/label/k8s.amazonaws.com/accelerator: aws-inferentia2
      k8s.io/cluster-autoscaler/node-template/resources/aws.amazon.com/neuron: "1"
      k8s.io/cluster-autoscaler/node-template/resources/aws.amazon.com/neuroncore: "2"
      k8s.io/cluster-autoscaler/node-template/resources/aws.amazon.com/neurondevice: "1"
      k8s.io/cluster-autoscaler/node-template/resources/cpu: 31600m
      k8s.io/cluster-autoscaler/node-template/resources/ephemeral-storage: 448Gi
      k8s.io/cluster-autoscaler/node-template/resources/memory: 127700Mi

      k8s.io/cluster-autoscaler/node-template/taint/flyte.org/node-role: worker:NoSchedule
```

As you can see in the above, we're creating a new instance configuration, which is _not_ a GPU instance, but an Inferentia instance.
This means we need to define our own autoscaling_tags, consult the Union AI team for the correct values.

### Setup Neuronx Kubernetes Plugin
In order to detect Neuronx enabled devices like Inferentia v2, or Trainium; we need to install the Neuronx Kubernetes plugin.
This plugin will also automatically update the accelerated Node with the correct resource quantities available; which can then be requested
by Flyte tasks and automatically attached.
Example configuration files are available in the `k8s` directory.
```bash
kubectl apply -f k8s/k8s-neuronx-plugin.yaml
kubectl apply -f k8s/k8s-neuronx-plugin-rbac.yaml
```

After these plugin are installed, you can verify that the plugin is running correctly by running:
by launching an inf2 node in the above nodegroup, and ensuring that the k8s-neuronx-plugin is currently operating on that node.
You should see the following in the `capacity` section of the node description:
```yaml
│ Capacity:                                                                                                             │
│   aws.amazon.com/neuron:        1                                                                                     │
│   aws.amazon.com/neuroncore:    2                                                                                     │
│   aws.amazon.com/neurondevice:  1                                                                                     │
│   cpu:                          32                                                                                    │
│   ephemeral-storage:            524275692Ki                                                                           │
│   hugepages-1Gi:                0                                                                                     │
│   hugepages-2Mi:                0                                                                                     │
│   memory:                       129215308Ki                                                                           │
│   pods:                         234
```

### Defining your Flyte Task Pod Template
In order to use the Neuronx plugin, you need to define a pod template that requests the Neuronx resources.
You must also have the neuronx custom system dependencies installed; you can find a base image available at `ghcr.io/unionai-oss/neuronx:2.0`

The following pod_template is used, however in the future this will be built-in to the Flytekit Accelerator field:
```python
from flytekit import PodTemplate
from kubernetes.client import V1PodSpec, V1Container
p_template = PodTemplate(
    primary_container_name="container",
    pod_spec=V1PodSpec(
        containers=[
            V1Container(
                name="container",
                resources={
                    "requests": {"aws.amazon.com/neuron": 1, "memory": "10Gi"},
                    "limits": {"aws.amazon.com/neuron": 1, "memory": "10Gi"},
                }
            )
        ],
        node_selector={"k8s.amazonaws.com/accelerator": "aws-inferentia2"},
    )
)
```

