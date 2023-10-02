# """Script to run all the workflows on a remote Flyte cluster.
#
# NOTE: This script assumes that:
# 1. You have the appropriate configuration to run executions on the remote cluster.
# 2. The workflows are registered in the cluster.
# """

import os
import pytest
from pathlib import Path
from .cases import WorkflowCase, WORKFLOW_CASES
from flytekit.remote import FlyteRemote
from flytekit.configuration import Config
from ..config import target_project, target_domain


class TestWorkflow:
    @classmethod
    def setup_class(cls):
        # get config path from environment variable, or use the uctl default
        cls.CONFIG_PATH = os.environ.get(
            "FLYTECTL_CONFIG",
            str(Path.home() / ".uctl" / "config.yaml")
        )

        cls.remote = FlyteRemote(
            config=Config.auto(cls.CONFIG_PATH),
            default_project=target_project,
            default_domain=target_domain,
        )

    @pytest.mark.parametrize("wf_case", WORKFLOW_CASES)
    def test_workflow(self, wf_case: WorkflowCase):
        flyte_wf = self.remote.fetch_workflow(name=wf_case.workflow.name)
        print(f"Running workflow {flyte_wf.name} with inputs {wf_case.inputs}")
        execution = self.remote.execute(flyte_wf, inputs=wf_case.inputs)
        url = self.remote.generate_console_url(execution)
        print(f"Execution URL: {url}")
        execution = self.remote.wait(execution)
        assert execution.closure.phase == 4
