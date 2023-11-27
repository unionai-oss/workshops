"""Flyte LLama workflows."""

import os
from pathlib import Path
from typing import List, Optional

from flytekit import task, workflow, current_context, Resources, Secret, ImageSpec
from flytekit.loggers import logger
from flytekit.types.directory import FlyteDirectory

import flyte_llm

# Union Tenant
SECRET_GROUP = "arn:aws:secretsmanager:us-east-2:356633062068:secret:"
WANDB_API_SECRET_KEY = "wand_api_key_tmls-PLs22C"
HF_HUB_API_SECRET_KEY = "huggingface_hub_api_key_tmls-CB6DVk"


image_spec = ImageSpec(
    name="flyte-llama-qlora",
    apt_packages=["git"],
    registry="ghcr.io/unionai-oss",
    requirements="requirements.txt",
    python_version="3.9",
    cuda="11.7.1",
    env={"VENV": "/opt/venv"},
)


@task(
    cache=True,
    cache_version="3",
    container_image=image_spec,
    requests=Resources(mem="8Gi", cpu="2", ephemeral_storage="8Gi"),
)
def create_dataset(additional_urls: Optional[List[str]] = None) -> FlyteDirectory:
    urls = [*flyte_llm.dataset.REPO_URLS, *(additional_urls or [])]

    ctx = current_context()
    working_dir = Path(ctx.working_directory)
    output_dir = working_dir / "dataset"
    repo_cache_dir = working_dir / "repo_cache"

    flyte_llm.dataset.create_dataset(urls, output_dir, repo_cache_dir)
    return FlyteDirectory(path=str(output_dir))


@task(
    cache=True,
    cache_version="20",
    container_image=image_spec,
    requests=Resources(mem="120Gi", cpu="44", gpu="8", ephemeral_storage="100Gi"),
    environment={
        "WANDB_PROJECT": "qlora-llama2-fine-tuning-tmls",
        "TRANSFORMERS_CACHE": "/tmp",
        "PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION": "python",
    },
    secret_requests=[
        Secret(
            group=SECRET_GROUP,
            key=WANDB_API_SECRET_KEY,
            mount_requirement=Secret.MountType.FILE,
        ),
        Secret(
            group=SECRET_GROUP,
            key=HF_HUB_API_SECRET_KEY,
            mount_requirement=Secret.MountType.FILE,
        ),
    ],
)
def train_task(
    dataset: FlyteDirectory,
    config: flyte_llm.train.TrainerConfig,
) -> FlyteDirectory:
    if int(os.environ.get("LOCAL_RANK", 0)) == 0:
        logger.info(f"Training Flyte Llama with params:\n{config}")
    pretrained_adapter = None
    if pretrained_adapter is not None:
        print(f"Downloading pretrained adapter {pretrained_adapter}")
        pretrained_adapter.download()

    wandb_run_name = os.environ.get("FLYTE_INTERNAL_EXECUTION_ID", "local")
    os.environ["WANDB_RUN_ID"] = wandb_run_name

    ctx = current_context()
    try:
        os.environ["WANDB_API_KEY"] = ctx.secrets.get(SECRET_GROUP, WANDB_API_SECRET_KEY)
    except ValueError:
        pass

    dataset.download()
    config.data_dir = dataset.path

    try:
        hf_auth_token = ctx.secrets.get(SECRET_GROUP, HF_HUB_API_SECRET_KEY)
    except ValueError:
        hf_auth_token = None

    flyte_llm.train.train(config, pretrained_adapter, hf_auth_token)
    return FlyteDirectory(path=str(config.output_dir))

@task(
    container_image=image_spec,
    requests=Resources(mem="120Gi", cpu="44", gpu="8", ephemeral_storage="100Gi"),
    environment={
        "WANDB_PROJECT": "qlora-llama2-fine-tuning-tmls",
        "TRANSFORMERS_CACHE": "/tmp",
        "PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION": "python",
    },
    secret_requests=[
        Secret(
            group=SECRET_GROUP,
            key=WANDB_API_SECRET_KEY,
            mount_requirement=Secret.MountType.FILE,
        ),
        Secret(
            group=SECRET_GROUP,
            key=HF_HUB_API_SECRET_KEY,
            mount_requirement=Secret.MountType.FILE,
        ),
    ],
)
# def inference(prompt: str) -> str:
#     return


@workflow
def train_workflow(
    config: flyte_llm.train.TrainerConfig,
) -> FlyteDirectory:
    dataset = create_dataset()
    model = train_task(
        dataset=dataset,
        config=config,
    )
    return model


@task(
    retries=3,
    cache=True,
    cache_version="0.0.4",
    container_image=image_spec,
    requests=Resources(mem="10Gi", cpu="1", ephemeral_storage="64Gi"),
    secret_requests=[
        Secret(
            group=SECRET_GROUP,
            key=HF_HUB_API_SECRET_KEY,
            mount_requirement=Secret.MountType.FILE,
        ),
    ],
)
def publish_model(
    model_dir: FlyteDirectory,
    config: flyte_llm.train.TrainerConfig,
) -> str:
    model_dir.download()
    model_dir = Path(model_dir.path)
    ctx = current_context()

    try:
        hf_auth_token = ctx.secrets.get(SECRET_GROUP, HF_HUB_API_SECRET_KEY)
    except Exception:
        hf_auth_token = None

    return flyte_llm.publish.publish_to_hf_hub(model_dir, config, hf_auth_token)


@workflow
def publish_model_workflow(
    model_dir: FlyteDirectory,
    config: flyte_llm.train.TrainerConfig,
) -> str:
    return publish_model(model_dir=model_dir, config=config)
