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
4. run `docker build -f Dockerfile -t your_image_registry.com/your_image_name:your_image_tag .`
5. run `docker push your_image_registry.com/your_image_name:your_image_tag`
6. update [imagespec.py](kaggle_data_processing/imagespec.py) with your image registry information
7. run `pyflyte run kaggle_data_processing/workflows/deduplication.py deduplication_wf --dataset_name="joelljungstrom/128k-airline-reviews" --file_name="AirlineReviews.csv"`

