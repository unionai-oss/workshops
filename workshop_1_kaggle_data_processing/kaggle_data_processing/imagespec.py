from flytekit import ImageSpec

registry_prefix = "ghcr.io/zeryx/"

dedupe_image = ImageSpec(
    name="core",
    base_image="ghcr.io/flyteorg/flytekit:py3.10-1.6.0",
    registry=registry_prefix,
    packages=["flytekit", "pandas==1.5.3"],
    apt_packages=["git"],

)

