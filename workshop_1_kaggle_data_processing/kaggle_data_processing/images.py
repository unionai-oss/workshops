from flytekit import ImageSpec
from .config import registry_prefix, dedupe_task_image_name


dedupe_task_image_spec = ImageSpec(
    name=dedupe_task_image_name,
    base_image="ghcr.io/flyteorg/flytekit:py3.10-1.6.0",
    registry=registry_prefix,
    packages=["flytekit", "pandas==1.5.3"],
    apt_packages=["git"],
)
