import pandas as pd
from flytekit import task, workflow, ContainerTask, kwtypes
from flytekit.types.file import FlyteFile
from ..imagespec import dedupe_image, default_image

get_dataset = ContainerTask(
    name="get_dataset",
    image="ghcr.io/zeryx/flytekit:kaggle-aaae",
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


@task
def get_credentials() -> str:
    with open("config.json") as f:
        config = f.read()
    return config


if dedupe_image.is_container:
    import pandas as pd


    @task(container_image=dedupe_image)
    def deduplicate_dataset(dataset: FlyteFile) -> pd.DataFrame:
        import pandas as pd
        df = pd.read_csv(dataset)
        df.drop_duplicates(inplace=True)
        return df


    @workflow
    def wf(dataset_name: str, file_name: str) -> pd.DataFrame:
        config = get_credentials()
        dataset: FlyteFile = get_dataset(dataset_name=dataset_name, file_name=file_name, kaggle_config=config)
        deduped_data = deduplicate_dataset(dataset=dataset)
        return deduped_data
