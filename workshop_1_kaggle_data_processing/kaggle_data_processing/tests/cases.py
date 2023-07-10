import pandas as pd
from typing import Any, Dict, NamedTuple, Tuple, Type
from flytekit.core.workflow import PythonFunctionWorkflow
from ..workflows.deduplication import deduplication_wf


class WorkflowCase(NamedTuple):
    workflow: PythonFunctionWorkflow
    inputs: Dict[str, Any]
    expected_output_types: Tuple[Type, ...]


WORKFLOW_CASES = [
    WorkflowCase(
        workflow=deduplication_wf,
        inputs={"dataset_name": "joelljungstrom/128k-airline-reviews", "file_name": "AirlineReviews.csv"},
        expected_output_types=(pd.DataFrame,)
    ),
    WorkflowCase(
        workflow=deduplication_wf,
        inputs={"dataset_name": "ankitkumar2635/sentiment-and-emotions-of-tweets", "file_name": "sentiment-emotion-labelled_Dell_tweets.csv"},
        expected_output_types=(pd.DataFrame,)
    ),
]
