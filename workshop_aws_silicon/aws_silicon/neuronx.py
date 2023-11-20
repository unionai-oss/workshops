"""A simple Flyte example that uses specialized hardware."""
import time
import os, pathlib
from flytekit import task, workflow, PodTemplate, kwtypes, ImageSpec
from kubernetes.client import V1PodSpec, V1Container


"""
A kubernetes Pod Template that allows a user to select the instance type 
of the node that the task will run on. 
This is useful for tasks that require a specialized nodegroup.
"""

p_template = PodTemplate(
    primary_container_name="container",
    pod_spec=V1PodSpec(
        containers=[
            V1Container(
                name="container",
                resources={
                    "requests": {"aws.amazon.com/neuroncore": 1, "memory": "10Gi"},
                    "limits": {"aws.amazon.com/neuroncore": 1, "memory": "10Gi"},
                }
            )
        ],
        node_selector={"k8s.amazonaws.com/accelerator": "aws-inferentia2"},
    )
)

dashboard_image = ImageSpec(
    packages=["flytekit",
              "matplotlib",
              "seaborn",
              "flytekitplugins-envd",
              "flytekitplugins-papermill"],
    registry="ghcr.io/unionai-oss",
    name="neuronx-dashboard"
)

neuronx_image = ImageSpec(
    # packages=["flytekit>=1.10", "torch==2.0", "torchvision"],
    base_image="ghcr.io/unionai-oss/neuronx:2.0",
    registry="ghcr.io/unionai-oss",
    name="neuronx-resnet50"
)



@task(container_image=neuronx_image)
def infer_on_cpu() -> dict:
    """
    This task will run on a CPU node and will be used as a baseline for comparison.
    It uses the same dependencies as the neuronx task, but doesn't run on a neuronx accelerated node.
    :return:
    output: dict - contains the inference time and the output vector of the model as a List[List[Float]].
    """
    import torch
    from PIL import Image
    import requests
    from torchvision import models
    from torchvision.transforms import functional
    model = models.resnet50(pretrained=True)
    model.eval()

    url = "http://images.cocodataset.org/val2017/000000039769.jpg"
    image = Image.open(requests.get(url, stream=True).raw)
    image = image.convert('RGB')
    image = functional.resize(image, (224, 224))
    image = functional.to_tensor(image)
    image = torch.unsqueeze(image, 0)
    output = {}
    t0 = time.time()
    output_cpu = model(image)
    t1 = time.time()
    output["cpu_time"] = t1 - t0
    output["result"] = output_cpu.detach().numpy().tolist()
    return output

@task(pod_template=p_template, container_image=neuronx_image)
def infer_on_inf2() -> dict:
    """
    This task will run on a neuronx accelerated inf2 node, with Inferentia-v2 AWS Accelerators attached.
    This leverages the torch_neuronx library to trace the model and compile it for the Inferentia-v2 chip, before running inference.
    :return:
    """
    import torch
    import torch_neuronx
    from PIL import Image
    import requests
    from torchvision import models
    from torchvision.transforms import functional
    model = models.resnet50(pretrained=True)  # could also choose from resnet18, resnet34, resnet101, resnet152
    model.eval()

    url = "http://images.cocodataset.org/val2017/000000039769.jpg"
    image = Image.open(requests.get(url, stream=True).raw)
    image = image.convert('RGB')
    image = functional.resize(image, (224, 224))
    image = functional.to_tensor(image)
    image = torch.unsqueeze(image, 0)

    output = {}

    # Compile the model
    model_neuron = torch_neuronx.trace(model, image)
    t0 = time.time()
    output_neuron = model_neuron(image)
    t1 = time.time()

    output["inf2_time"] = t1 - t0
    output["result"] = output_neuron.detach().numpy().tolist()

    return output

if dashboard_image.is_container():
    from flytekitplugins.papermill import NotebookTask
    generate_deck = NotebookTask(
        name="resnet50-inference-comparison",
        notebook_path=os.path.join(pathlib.Path(__file__).parent.parent.absolute(), "notebooks/dashboard.ipynb"),
        render_deck=True,
        enable_deck=True,
        inputs=kwtypes(inf2=dict, cpu=dict),
        container_image=dashboard_image
    )

    @workflow
    def resnet50_infer_wf():
        inf2_output = infer_on_inf2()
        cpu_output = infer_on_cpu()
        generate_deck(inf2=inf2_output, cpu=cpu_output)

