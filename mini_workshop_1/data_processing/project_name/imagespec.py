from flytekit import ImageSpec


default_image = ImageSpec(
    name="flytekit",
    base_image="ghcr.io/flyteorg/flytekit:py3.10-1.6.0",
    registry="pingsutw",
    packages=["flytekit"]
)

dedupe_image = ImageSpec(
    name="flytekit",
    base_image="ghcr.io/flyteorg/flytekit:py3.10-1.6.0",
    registry="pingsutw",
    packages=["flytekit", "pandas"]
)
