# Deploying models to Nvidia Triton

This workshop/example showcases how to:
- Deploy a Triton Server with necessary backends
- Register a trained model in Flyte, and deploy it to Triton
- Perform batch inference on a model deployed to a Triton Inference Server


## Prerequisites
- Access to an Ec2 instance with Nvidia Triton running
- AWS security policy permitting your local IP, or your Flyte Cluster IP to access the Triton Server
- A model from Huggingface Hub that you would like to deploy to Triton

## Steps
1. Clone this repository
2. Add your IP to the EC2 instance `"ec2-18-118-218-187.us-east-2.compute.amazonaws.com"` to the AWS
3. Install the requirements in [requirements.txt](requirements.txt)
4. run `pyflyte run --remote triton_workflows/main.py register_model` to register the model in Flyte
5. Run `pyflyte run flyte_workflows/main.py make_batch_inference_request --inputs="hello brian. The quick brown fox. Hello ." --model_name="llama2_7b_chat" --hf_hub_model_name="llama2_7b_chat" --model_version=1` to make your batch inference request, from your local environment
