import flytekit
from flytekit import task, workflow, ContainerTask, kwtypes, Resources, TaskMetadata
from flytekit.types.file import FlyteFile
from flytekit import Secret
from ..imagespec import dedupe_image, registry_prefix

SECRET_GROUP = "arn:aws:secretsmanager:<your-aws-region>:<your-aws-account>:"
SECRET_KEY = "<your-secret-org>/<your-secret-name"

# noinspection PyTypeChecker
get_dataset = ContainerTask(
    name="get_dataset",
    image=f"{registry_prefix}/core:kaggle",
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
    ],
    metadata=TaskMetadata(retries=5)
)


@task(
    secret_requests=[
        Secret(
            group=SECRET_GROUP,
            key=SECRET_KEY,
            mount_requirement=Secret.MountType.FILE)
    ],
)
def get_credentials() -> str:
    config = flytekit.current_context().secrets.get(SECRET_GROUP, SECRET_KEY)
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


    @workflow
    def deduplication_wf(dataset_name: str, file_name: str) -> pd.DataFrame:
        config = get_credentials()
        # noinspection PyTypeChecker
        dataset: FlyteFile = get_dataset(dataset_name=dataset_name, file_name=file_name, kaggle_config=config)
        deduped_data = deduplicate_dataset(dataset=dataset)
        # noinspection PyTypeChecker
        return deduped_data
