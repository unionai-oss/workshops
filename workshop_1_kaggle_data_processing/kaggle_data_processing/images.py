from flytekit import ImageSpec

registry_prefix = "ghcr.io/<your-username>/"


# This image is used by the ContainerTask obtaining the dataset with the Kaggle API
get_dataset_package_name_tag = "dedupe:latest"


# This image is used by the task deduplicating the dataset, and is utilized in the ImageSpec below
dedupe_image_package_name = "default"

dedupe_image = ImageSpec(
    name=dedupe_image_package_name,
    base_image="ghcr.io/flyteorg/flytekit:py3.10-1.6.0",
    registry=registry_prefix,
    packages=["flytekit", "pandas==1.5.3"],
    apt_packages=["git"],

)

