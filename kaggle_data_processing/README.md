# Getting Data from Kaggle Workshop

This workshop will show you how to get data from Kaggle and process it for use in your projects.


## Features
The following advanced Flyte features will be covered:
- Raw ContainerTasks
- AWS Secrets Manager integration
- Imagespec
- Integration Testing
- CI/CD

## Prerequisites
- [Docker](https://docs.docker.com/get-docker/)
- [Flyte](https://docs.flyte.org/en/latest/getting_started/installation.html)
- ghcr.io / Hosted image Registry access
- An AWS-based Flyte cluster (GCP and Azure will be supported in the future by this workshop)

## Setup
1. Clone this repository
2. Create a [Kaggle Account](https://www.kaggle.com/)
3. Create a [Kaggle API Token](https://www.kaggle.com/docs/api#getting-started-installation-&-authentication)
4. Update [images.py](kaggle_data_processing/images.py) with your image registry information, you may redefine both package names
5. Ensure that both the Deduplication Package, and get_dataset Package are publicly available for Flyte to be able to access
5. Build an AWS Secret containing your kaggle api auth, by following [this guide](https://docs.union.ai/integrations/enabling-aws-resources/enabling-aws-secrets-manager)
4. run `docker build --platform linux/amd64 -f Dockerfile -t your_image_registry.com/dedupe:latest .`
5. run `docker push your_image_registry.com/dedupe:latest`
6. update your dependencies by installing all the local dependencies `pip install -r requirements.txt`
6. update [images.py](kaggle_data_processing/images.py) with your image registry information
7. run `pyflyte register kaggle_data_processing --project <your-project-name> --domain <your-domain>`

## Pytest
1. Perform all steps in [Setup](#setup)
2. Update [test_workflows.py](tests/test_workflows.py) with your project and domain of the registered workflow
3. Run `pytest` and wait for the tests to complete
