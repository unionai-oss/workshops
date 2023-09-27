from flytekit import ImageSpec

# Your image registry url, if using ghcr.io, this will be "ghcr.io/<your-username>"
registry_prefix = "ghcr.io/<your-github-organization>"


# This image is used by the ContainerTask obtaining the dataset with the Kaggle API
get_dataset_package_name_tag = "get_dataset:latest"


# This image is used by the task deduplicating the dataset, and is utilized in the ImageSpec below
dedupe_image_package_name = "dedupe"

dedupe_image = ImageSpec(
    name=dedupe_image_package_name,
    base_image="ghcr.io/flyteorg/flytekit:py3.10-1.6.0",
    registry=registry_prefix,
    packages=["flytekit", "pandas==1.5.3"],
    apt_packages=["git"],
)

