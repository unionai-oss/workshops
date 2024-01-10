from typing import List

from flytekit.types.directory import FlyteDirectory
from tritonclient.http import InferenceServerClient, InferInput
from transformers import AutoTokenizer, AutoModelForTokenClassification
from flytekit import workflow, task, ImageSpec, Resources
import torch as th
import numpy as np
import os


image = ImageSpec(
    requirements="requirements.txt",
    registry="ghcr.io/unionai-oss",
    name="trition-deployer",
    base_image="nvidia/cuda:12.3.1-runtime-ubuntu20.04",
    python_version="3.10"
)


def generate_config_pbtxt(model_name, input_shapes, output_shapes):
    inputs_config = ",\n".join(
        f"""
    {{
        name: "{name}"
        data_type: TYPE_INT32  # or appropriate data type
        dims: {list(shape)}  # Exclude the batch dimension
    }}
        """ for name, shape in input_shapes.items()
    )

    outputs_config = ",\n".join(
        f"""
        {{
            name: "{name}"
            data_type: TYPE_FP32  # or appropriate data type
            dims: {list(shape)}  # Exclude the batch dimension
        }}
        """ for name, shape in output_shapes.items()
    )

    config = f"""
    name: "{model_name}"
    backend: "pytorch"
    max_batch_size: 0  # 0 for dynamic batching
    
    input [
    {inputs_config}
    ]
    
    output [
    {outputs_config}
    ]
    
    parameters: {{
    key: "ENABLE_JIT_EXECUTOR"
    value: {{
        string_value: "false"
        }}
    }}
    dynamic_batching {{
    max_queue_delay_microseconds: 10000000
   }}
    instance_group [
      {{
        kind: KIND_GPU
        count: 10
      }}
    ]

    """
    return config


@task(container_image=image, requests=Resources(mem="25Gi", gpu="1"))
def register_hf_text_classifier(hf_hub_model_name: str, model_name: str, model_registry_uri: str) -> FlyteDirectory:
    version = 1
    model = AutoModelForTokenClassification.from_pretrained(hf_hub_model_name, torchscript=True)
    model = model.to("cuda")
    tokenizer = AutoTokenizer.from_pretrained(hf_hub_model_name)
    dummy_input = tokenizer("foo bar", padding='max_length', max_length=128, truncation=True, return_tensors="pt")
    dummy_input = {key: value.to("cuda") for key, value in dummy_input.items()}
    with th.no_grad():
        traced_model = th.jit.trace(model, example_inputs=[ value for key, value in dummy_input.items()])
        output = traced_model(**dummy_input)
    inputs_and_shapes = {key: value.shape for key, value in dummy_input.items()}
    outputs_and_shapes = {}
    if isinstance(output, tuple):
            for i, tensor in enumerate(output):
                    outputs_and_shapes[f"output_{i}"] = tensor.shape
    else:
        outputs_and_shapes["output"] = output.shape

    os.makedirs(f"/tmp/{model_name}/{version}", exist_ok=True)

    config = generate_config_pbtxt(model_name, inputs_and_shapes, outputs_and_shapes)
    traced_model.save(f"/tmp/{model_name}/{version}/model.pt")
    with open(f"/tmp/{model_name}/config.pbtxt", "w") as f:
        f.write(config)
    return FlyteDirectory(path=f"/tmp/{model_name}", remote_directory=f"{model_registry_uri}/{model_name}")

@task(container_image=image)
def make_inference_request(input: str, model_name: str, hf_hub_model_name: str, model_version: int) -> np.ndarray:
    tokenizer = AutoTokenizer.from_pretrained(hf_hub_model_name)
    client = InferenceServerClient("ec2-18-118-218-187.us-east-2.compute.amazonaws.com:8000")
    encoded = tokenizer(input, padding='max_length', max_length=128, truncation=True)
    encoded = {key: np.asarray(value, dtype=np.int32).reshape(1, -1) for key, value in encoded.items() }
    model_inputs = []
    for key, value in encoded.items():
        model_inputs.append(InferInput(key, value.shape, "INT32"))
        model_inputs[-1].set_data_from_numpy(value)
    infer_result = client.infer(model_name, model_inputs, model_version=str(model_version))
    result = infer_result.as_numpy("output_0")
    return result

@task(container_image=image)
async def make_batch_inference_request(input: str, model_name: str, hf_hub_model_name: str, model_version: int, num_reqs: int) -> List[np.ndarray]:
    tokenizer = AutoTokenizer.from_pretrained(hf_hub_model_name, padding=True)
    client = InferenceServerClient("ec2-18-118-218-187.us-east-2.compute.amazonaws.com:8000")
    async_results = []
    for _ in range(num_reqs):
        encoded = tokenizer(input, padding='max_length', max_length=128, truncation=True)
        encoded = {key: np.asarray(value, dtype=np.int32).reshape(1, -1) for key, value in encoded.items()}
        model_inputs = []
        for key, value in encoded.items():
            model_inputs.append(InferInput(key, value.shape, "INT32"))
            model_inputs[-1].set_data_from_numpy(value)
        async_result = client.async_infer(model_name, model_inputs, model_version=str(model_version))
        async_results.append(async_result)
    results = [(async_result.get_result()).as_numpy("output_0") for async_result in async_results]
    return results



@workflow
def register_model(model_name: str="distilroberta-finetuned-financial-news-sentiment-analysis",
                   model_registry_uri: str="s3://union-oc-production-demo/triton-model-registry",
                   hf_hub_model_name: str="mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis") -> FlyteDirectory:
    return register_hf_text_classifier(hf_hub_model_name=hf_hub_model_name, model_name=model_name, model_registry_uri=model_registry_uri)
