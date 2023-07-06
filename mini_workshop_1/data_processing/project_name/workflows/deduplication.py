import glob
import os
import zipfile
import pandas as pd
from flytekit import task, workflow, ContainerTask, kwtypes
from flytekit.types.file import FlyteFile
from ..imagespec import dedupe_image, default_image
from flytekit.types.directory import FlyteDirectory
get_dataset = ContainerTask(
    name="get_dataset",
    image="ghcr.io/zeryx/flytekit:kaggle-aaae",
    input_data_dir="/var/inputs",
    output_data_dir="/var/outputs",
    inputs=kwtypes(dataset_name=str, file_name=str, kaggle_config=str),
    outputs=kwtypes(dataset=FlyteDirectory),
    command=[
        "./get_dataset.sh",
        "{{.inputs.dataset_name}}",
        "{{.inputs.file_name}}",
        "{{.inputs.kaggle_config}}",
        "/var/outputs/dataset"
    ]
)


@task
def get_credentials() -> str:
    with open("config.json") as f:
        config = f.read()
    return config


if dedupe_image.is_container:
    import pandas as pd


    @task(container_image=dedupe_image)
    def deduplicate_dataset(dataset: FlyteDirectory) -> pd.DataFrame:
        dataset.download()
        files = glob.glob(os.path.join(dataset.path, "*"))
        zf = zipfile.ZipFile(files[0])
        df = pd.read_csv(zf.open('crawl-300d-2M.vec'))
        df.drop_duplicates(inplace=True)
        return df


    @workflow
    def wf(dataset_name: str, file_name: str) -> pd.DataFrame:
        config = get_credentials()
        dataset: FlyteDirectory = get_dataset(dataset_name=dataset_name, file_name=file_name, kaggle_config=config)
        deduped_data = deduplicate_dataset(dataset=dataset)
        return deduped_data
