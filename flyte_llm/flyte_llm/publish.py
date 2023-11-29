import yaml
from dataclasses import asdict

from io import BytesIO
from pathlib import Path
from typing import Optional

import huggingface_hub as hh

from flyte_llm.train import TrainerConfig, PublishConfig


MODEL_CARD_TEMPLATE = """
---
{model_card_content}
---

{readme_content}
""".strip()


def publish_to_hf_hub(
    model_dir: Path,
    adapter_name: str,
    config: TrainerConfig,
    hf_auth_token: str,
) -> str:
    # make sure the file can be downloaded
    publish_config: PublishConfig = config.publish_config

    hh.login(token=hf_auth_token)
    api = hh.HfApi()
    repo_id = f"Union-AI-OSS/{adapter_name}"

    repo_url = api.create_repo(repo_id, exist_ok=True)

    if publish_config.readme is not None:
        model_card_dict = publish_config.model_card.to_dict()

        config_dict = asdict(config)

        dataset_path = config_dict.get("data_path", None)
        if dataset_path:
            model_card_dict["datasets"] = [config_dict.get("data_path")]

        readme_str = MODEL_CARD_TEMPLATE.format(
            model_card_content=yaml.dump(model_card_dict),
            readme_content=publish_config.readme,
        )
        api.upload_file(
            path_or_fileobj=BytesIO(readme_str.encode()),
            path_in_repo="README.md",
            repo_id=repo_id,
        )

    api.upload_folder(
        repo_id=repo_id,
        folder_path=model_dir,
        ignore_patterns=["flyte*", "models--*", "tmp*"]
    )
    return str(repo_url)
