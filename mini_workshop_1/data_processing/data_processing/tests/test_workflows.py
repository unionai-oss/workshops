"""Script to run all the workflows on a remote Flyte cluster.

NOTE: This script assumes that:
1. You have the appropriate configuration to run executions on the remote cluster.
2. The workflows are registered in the cluster.
"""

import os
import logging
from pathlib import Path

import pandas as pd

from .cases import WorkflowCase, WORKFLOW_CASES
from flytekit.remote import FlyteRemote
from flytekit.configuration import Config
import pytest

logger = logging.getLogger(__name__)

CONFIG_PATH = os.environ.get(
    "UCTL_CONFIG",
    str(Path.home() / ".uctl" / "config.yaml")
)

remote = FlyteRemote(
    config=Config.auto(CONFIG_PATH),
    default_project="flytetester",
    default_domain="development",
)


@pytest.mark.parametrize("wf_case", WORKFLOW_CASES)
def test_workflow(wf_case: WorkflowCase):
    flyte_wf = remote.fetch_workflow(name=wf_case.workflow.name)
    logger.info(f"Running workflow {flyte_wf.name} with inputs {wf_case.inputs}")
    execution = remote.execute(flyte_wf, inputs=wf_case.inputs)
    url = remote.generate_console_url(execution)
    logger.info(f"Execution URL: {url}")
    execution = remote.wait(execution)
    ## Make sure that your aws credentials are set up correctly to download from S3 locally
    # data_file = execution.outputs.get("o0", as_type=pd.DataFrame)
    # assert isinstance(data_file, pd.DataFrame)
    assert execution.closure.phase == 4
