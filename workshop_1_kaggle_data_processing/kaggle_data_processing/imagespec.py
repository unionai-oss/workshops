from flytekit import ImageSpec

dedupe_image = ImageSpec(
    name="core",
    base_image="ghcr.io/flyteorg/flytekit:py3.10-1.6.0",
    registry="ghcr.io/zeryx",
    packages=["flytekit", "pandas==1.5.3"],
    apt_packages=["git"],

)
