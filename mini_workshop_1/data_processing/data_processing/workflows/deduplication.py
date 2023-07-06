from flytekit import task, workflow, ContainerTask, kwtypes, Resources
from flytekit.types.file import FlyteFile
from ..imagespec import dedupe_image
"""
This is a project that deduplicates a dataset stored on Kaggle.
As Kaggle requires CLI access to download datasets, we use a container task to download the dataset.
"""
get_dataset = ContainerTask(
    name="get_dataset",
    image="ghcr.io/zeryx/core:kaggle",
    input_data_dir="/var/inputs",
    output_data_dir="/var/outputs",
    inputs=kwtypes(dataset_name=str, file_name=str, kaggle_config=str),
    outputs=kwtypes(dataset=FlyteFile),
    command=[
        "./get_dataset.sh",
        "{{.inputs.dataset_name}}",
        "{{.inputs.file_name}}",
        "{{.inputs.kaggle_config}}",
        "/var/outputs/dataset"
    ]
)


"""
This is a task that reads a config file from the local filesystem.
You can replace this with an AWS Secrets Manager setup, and simply read the secret from the filesystem.
"""
@task
def get_credentials() -> str:
    with open("kaggle.json") as f:
        config = f.read()
    return config


# As pandas may not be installed locally, we only import it if we are running in a container.
# We still validate the workflow, but we don't fully trace the IO.
# We do that with the `.is_container` property of imagespec objects.
if dedupe_image.is_container:
    import pandas as pd
    @task(container_image=dedupe_image, requests=Resources(cpu="2", mem="10Gi", ephemeral_storage="10Gi"))
    def deduplicate_dataset(dataset: FlyteFile) -> pd.DataFrame:
        print("getting dataset as csv")
        df = pd.read_csv(dataset, on_bad_lines='skip')
        print("loaded csv into dataframe")
        df.drop_duplicates(inplace=True)
        return df


    """
    This workflow deduplicates a dataset stored on Kaggle.
    As this workflow contains pandas dependencies, we don't fully trace the IO during registration.
    """
    @workflow
    def deduplication_wf(dataset_name: str, file_name: str) -> pd.DataFrame:
        config = get_credentials()
        dataset: FlyteFile = get_dataset(dataset_name=dataset_name, file_name=file_name, kaggle_config=config)
        deduped_data = deduplicate_dataset(dataset=dataset)
        return deduped_data
