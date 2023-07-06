import pandas as pd
from typing import Any, Callable, Dict, NamedTuple, Tuple, Type
from flytekit.core.workflow import PythonFunctionWorkflow
from mini_workshop_1.data_processing.src.workflows.deduplication import deduplication_wf


class WorkflowCase(NamedTuple):
    workflow: PythonFunctionWorkflow
    inputs: Dict[str, Any]
    expected_output_types: Tuple[Type, ...]


WORKFLOW_CASES = [
    WorkflowCase(
        workflow=deduplication_wf,
        inputs={"dataset_name": "yekenot/fasttext-crawl-300d-2m", "file_name": "crawl-300d-2M.vec"},
        expected_output_types=(pd.DataFrame,)
    )
]
