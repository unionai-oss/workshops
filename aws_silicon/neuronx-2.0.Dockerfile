FROM python:3.8-slim-buster

WORKDIR /root
ENV VENV /opt/venv
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONPATH /root

RUN apt-get update && apt-get install -y build-essential
RUN apt-get install -y --no-install-recommends \
    gnupg2 \
    wget

# Neuron repos
ARG APT_REPO=https://apt.repos.neuron.amazonaws.com
ARG PIP_REPO=https://pip.repos.neuron.amazonaws.com

# Python won’t try to write .pyc or .pyo files on the import of source modules
# Force stdin, stdout and stderr to be totally unbuffered. Good for logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=UTF-8
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/opt/aws/neuron/lib"
ENV LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/opt/amazon/openmpi/lib64"
ENV LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/usr/local/lib"

RUN apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    cmake \
    curl \
    git \
    libopencv-dev \
    libglib2.0-0 \
    libgl1-mesa-glx \
    libsm6 \
    libxext6 \
    libxrender-dev \
    wget \
    unzip \
    zlib1g-dev \
    openssl \
    libssl-dev \
    libgdbm-dev \
    libc6-dev \
    libbz2-dev \
    tk-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

RUN echo "deb $APT_REPO focal main" > /etc/apt/sources.list.d/neuron.list
RUN wget -qO - $APT_REPO/GPG-PUB-KEY-AMAZON-AWS-NEURON.PUB | apt-key add -

RUN apt-get update \
 && apt-get install -y \
    aws-neuronx-tools \
    aws-neuronx-collectives \
    aws-neuronx-runtime-lib \
 && rm -rf /var/lib/apt/lists/* \
 && rm -rf /tmp/tmp* \
 && apt-get clean

WORKDIR /

RUN mkdir -p /etc/pki/tls/certs && cp /etc/ssl/certs/ca-certificates.crt /etc/pki/tls/certs/ca-bundle.crt



# NOTE: Preceding Docker statements build a standard Neuron-compatible container with EFA support. Add your
#   training script and dependencies below this line


ENV VENV /opt/venv
# Virtual environment
RUN python3 -m venv ${VENV}
ENV PATH="${VENV}/bin:$PATH"

RUN pip config set global.extra-index-url $PIP_REPO
RUN pip install --pre torch-neuronx==2.0.* neuronx-cc==2.* torchvision --extra-index-url $PIP_REPO
RUN pip install -U flytekit
RUN pip install protobuf==3.20
# Install Python dependencies
COPY requirements.txt /root
# RUN pip install -r /root/requirements.txt

# Copy the actual code
COPY . /root

# This tag is supplied by the build script and will be used to determine the version
# when registering tasks, workflows, and launch plans
ARG tag
ENV FLYTE_INTERNAL_IMAGE $tag
