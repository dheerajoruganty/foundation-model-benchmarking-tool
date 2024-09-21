# Benchmark models on EC2

You can use `FMBench` to benchmark models on hosted on EC2. This can be done in one of two ways:

- Deploy the model on your EC2 instance independantly of `FMBench` and then benchmark it through the [Bring your own endpoint](#bring-your-own-endpoint-aka-support-for-external-endpoints) mode.
- Deploy the model on your EC2 instance through `FMBench` and then benchmark it.
 
The steps for deploying the model on your EC2 instance are described below. 

👉 In this configuration both the model being benchmarked and `FMBench` are deployed on the same EC2 instance.

Create a new EC2 instance suitable for hosting an LMI as per the steps described [here](misc/ec2_instance_creation_steps.md). _Note that you will need to select the correct AMI based on your instance type, this is called out in the instructions_.

The steps for benchmarking on different types of EC2 instances (GPU/CPU/Neuron) and different inference containers differ slightly. These are all described below.

## Benchmarking options on EC2
- [Benchmarking on an instance type with NVIDIA GPUs or AWS Chips](#benchmarking-on-an-instance-type-with-nvidia-gpus-or-aws-chips)
- [Benchmarking on an CPU instance type with AMD processors](#benchmarking-on-an-cpu-instance-type-with-amd-processors)
- [Benchmarking on an CPU instance type with Intel processors](#benchmarking-on-an-cpu-instance-type-with-intel-processors)

- [Benchmarking the Triton inference server on GPU instances](#benchmarking-the-triton-inference-server-on-gpu-instances)

## Benchmarking on an instance type with NVIDIA GPUs or AWS Chips

1. Connect to your instance using any of the options in EC2 (SSH/EC2 Connect), run the following in the EC2 terminal. This command installs Anaconda on the instance which is then used to create a new `conda` environment for `FMBench`. See instructions for downloading anaconda [here](https://www.anaconda.com/download)

    ```{.bash}
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
    bash Miniconda3-latest-Linux-x86_64.sh -b  # Run the Miniconda installer in batch mode (no manual intervention)
    rm -f Miniconda3-latest-Linux-x86_64.sh    # Remove the installer script after installation
    eval "$(/home/$USER/miniconda3/bin/conda shell.bash hook)" # Initialize conda for bash shell
    conda init  # Initialize conda, adding it to the shell  
    ```

1. Install `docker-compose`.

    ```{.bash}
    sudo apt-get update
    sudo apt-get install --reinstall docker.io -y
    sudo apt-get install -y docker-compose
    docker compose version 
    ```

1. Setup the `fmbench_python311` conda environment.

    ```{.bash}
    conda create --name fmbench_python311 -y python=3.11 ipykernel
    source activate fmbench_python311;
    pip install -U fmbench
    ```

1. Create local directory structure needed for `FMBench` and copy all publicly available dependencies from the AWS S3 bucket for `FMBench`. This is done by running the `copy_s3_content.sh` script available as part of the `FMBench` repo. Replace `/tmp` in the command below with a different path if you want to store the config files and the `FMBench` generated data in a different directory.

    ```{.bash}
    curl -s https://raw.githubusercontent.com/aws-samples/foundation-model-benchmarking-tool/main/copy_s3_content.sh | sh -s -- /tmp
    ```

1. To download the model files from HuggingFace, create a `hf_token.txt` file in the `/tmp/fmbench-read/scripts/` directory containing the Hugging Face token you would like to use. In the command below replace the `hf_yourtokenstring` with your Hugging Face token.

    ```{.bash}
    echo hf_yourtokenstring > /tmp/fmbench-read/scripts/hf_token.txt
    ```

1. Run `FMBench` with a packaged or a custom config file. **_This step will also deploy the model on the EC2 instance_**. The `--write-bucket` parameter value is just a placeholder and an actual S3 bucket is not required. **_Skip to the next step if benchmarking for AWS Chips_**. You could set the `--tmp-dir` flag to an EFA path instead of `/tmp` if using a shared path for storing config files and reports.

    ```{.bash}
    fmbench --config-file /tmp/fmbench-read/configs/llama3/8b/config-ec2-llama3-8b.yml --local-mode yes --write-bucket placeholder --tmp-dir /tmp > fmbench.log 2>&1
    ```

1. For example, to run `FMBench` on a `llama3-8b-Instruct` model on an `inf2.48xlarge` instance, run the command 
command below. The config file for this example can be viewed [here](src/fmbench/configs/llama3/8b/config-ec2-llama3-8b-inf2-48xl.yml).

    ```{.bash}
    fmbench --config-file /tmp/fmbench-read/configs/llama3/8b/config-ec2-llama3-8b-inf2-48xl.yml --local-mode yes --write-bucket placeholder --tmp-dir /tmp > fmbench.log 2>&1
    ```

1. Open a new Terminal and do a `tail` on `fmbench.log` to see a live log of the run.

    ```{.bash}
    tail -f fmbench.log
    ```

1. All metrics are stored in the `/tmp/fmbench-write` directory created automatically by the `fmbench` package. Once the run completes all files are copied locally in a `results-*` folder as usual.

## Benchmarking on an CPU instance type with AMD processors

**_As of 2024-08-27 this has been tested on a `m7a.16xlarge` instance_**

1. Connect to your instance using any of the options in EC2 (SSH/EC2 Connect), run the following in the EC2 terminal. This command installs Anaconda on the instance which is then used to create a new `conda` environment for `FMBench`. See instructions for downloading anaconda [here](https://www.anaconda.com/download)

    ```{.bash}
    # Install Docker and Git using the YUM package manager
    sudo yum install docker git -y

    # Start the Docker service
    sudo systemctl start docker

    # Download the Miniconda installer for Linux
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
    bash Miniconda3-latest-Linux-x86_64.sh -b  # Run the Miniconda installer in batch mode (no manual intervention)
    rm -f Miniconda3-latest-Linux-x86_64.sh    # Remove the installer script after installation
    eval "$(/home/$USER/miniconda3/bin/conda shell.bash hook)" # Initialize conda for bash shell
    conda init  # Initialize conda, adding it to the shell
    ```

1. Setup the `fmbench_python311` conda environment.

    ```{.bash}
    # Create a new conda environment named 'fmbench_python311' with Python 3.11 and ipykernel
    conda create --name fmbench_python311 -y python=3.11 ipykernel

    # Activate the newly created conda environment
    source activate fmbench_python311

    # Upgrade pip and install the fmbench package
    pip install -U fmbench
    ```

1. Build the `vllm` container for serving the model. 

    1. 👉 The `vllm` container we are building locally is going to be references in the `FMBench` config file.

    1. The container being build is for CPU only (GPU support might be added in future).

        ```{.bash}
        # Clone the vLLM project repository from GitHub
        git clone https://github.com/vllm-project/vllm.git

        # Change the directory to the cloned vLLM project
        cd vllm

        # Build a Docker image using the provided Dockerfile for CPU, with a shared memory size of 4GB
        sudo docker build -f Dockerfile.cpu -t vllm-cpu-env --shm-size=4g .
        ```

1. Create local directory structure needed for `FMBench` and copy all publicly available dependencies from the AWS S3 bucket for `FMBench`. This is done by running the `copy_s3_content.sh` script available as part of the `FMBench` repo. Replace `/tmp` in the command below with a different path if you want to store the config files and the `FMBench` generated data in a different directory.

    ```{.bash}
    curl -s https://raw.githubusercontent.com/aws-samples/foundation-model-benchmarking-tool/main/copy_s3_content.sh | sh -s -- /tmp
    ```

1. To download the model files from HuggingFace, create a `hf_token.txt` file in the `/tmp/fmbench-read/scripts/` directory containing the Hugging Face token you would like to use. In the command below replace the `hf_yourtokenstring` with your Hugging Face token.

    ```{.bash}
    echo hf_yourtokenstring > /tmp/fmbench-read/scripts/hf_token.txt
    ```

1. Before running FMBench, add the current user to the docker group. Run the following commands to run Docker without needing to use `sudo` each time.

    ```{.bash}
    sudo usermod -a -G docker $USER
    newgrp docker
    ```

1. Install `docker-compose`.

    ```{.bash}
    DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
    mkdir -p $DOCKER_CONFIG/cli-plugins
    sudo curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o $DOCKER_CONFIG/cli-plugins/docker-compose
    sudo chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose
    docker compose version
    ```

1. Run `FMBench` with a packaged or a custom config file. **_This step will also deploy the model on the EC2 instance_**. The `--write-bucket` parameter value is just a placeholder and an actual S3 bucket is not required. You could set the `--tmp-dir` flag to an EFA path instead of `/tmp` if using a shared path for storing config files and reports.

    ```{.bash}
    fmbench --config-file /tmp/fmbench-read/configs/llama3/8b/config-ec2-llama3-8b-m7a-16xlarge.yml --local-mode yes --write-bucket placeholder --tmp-dir /tmp > fmbench.log 2>&1
    ```

1. Open a new Terminal and and do a `tail` on `fmbench.log` to see a live log of the run.

    ```{.bash}
    tail -f fmbench.log
    ```

1. All metrics are stored in the `/tmp/fmbench-write` directory created automatically by the `fmbench` package. Once the run completes all files are copied locally in a `results-*` folder as usual.


## Benchmarking on an CPU instance type with Intel processors

**_As of 2024-08-27 this has been tested on `c5.18xlarge` and `m5.16xlarge` instances_**

1. Connect to your instance using any of the options in EC2 (SSH/EC2 Connect), run the following in the EC2 terminal. This command installs Anaconda on the instance which is then used to create a new `conda` environment for `FMBench`. See instructions for downloading anaconda [here](https://www.anaconda.com/download)

    ```{.bash}
    # Install Docker and Git using the YUM package manager
    sudo yum install docker git -y

    # Start the Docker service
    sudo systemctl start docker

    # Download the Miniconda installer for Linux
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
    bash Miniconda3-latest-Linux-x86_64.sh -b # Run the Miniconda installer in batch mode (no manual intervention)
    rm -f Miniconda3-latest-Linux-x86_64.sh    # Remove the installer script after installation
    eval "$(/home/$USER/miniconda3/bin/conda shell.bash hook)" # Initialize conda for bash shell
    conda init  # Initialize conda, adding it to the shell
    ```

1. Setup the `fmbench_python311` conda environment.

    ```{.bash}
    # Create a new conda environment named 'fmbench_python311' with Python 3.11 and ipykernel
    conda create --name fmbench_python311 -y python=3.11 ipykernel

    # Activate the newly created conda environment
    source activate fmbench_python311

    # Upgrade pip and install the fmbench package
    pip install -U fmbench
    ```

1. Build the `vllm` container for serving the model. 

    1. 👉 The `vllm` container we are building locally is going to be references in the `FMBench` config file.

    1. The container being build is for CPU only (GPU support might be added in future).

        ```{.bash}
        # Clone the vLLM project repository from GitHub
        git clone https://github.com/vllm-project/vllm.git

        # Change the directory to the cloned vLLM project
        cd vllm

        # Build a Docker image using the provided Dockerfile for CPU, with a shared memory size of 12GB
        sudo docker build -f Dockerfile.cpu -t vllm-cpu-env --shm-size=12g .
        ```

1. Create local directory structure needed for `FMBench` and copy all publicly available dependencies from the AWS S3 bucket for `FMBench`. This is done by running the `copy_s3_content.sh` script available as part of the `FMBench` repo. Replace `/tmp` in the command below with a different path if you want to store the config files and the `FMBench` generated data in a different directory.

    ```{.bash}
    curl -s https://raw.githubusercontent.com/aws-samples/foundation-model-benchmarking-tool/main/copy_s3_content.sh | sh -s -- /tmp
    ```

1. To download the model files from HuggingFace, create a `hf_token.txt` file in the `/tmp/fmbench-read/scripts/` directory containing the Hugging Face token you would like to use. In the command below replace the `hf_yourtokenstring` with your Hugging Face token.

    ```{.bash}
    echo hf_yourtokenstring > /tmp/fmbench-read/scripts/hf_token.txt
    ```

1. Before running FMBench, add the current user to the docker group. Run the following commands to run Docker without needing to use `sudo` each time.

    ```{.bash}
    sudo usermod -a -G docker $USER
    newgrp docker
    ```

1. Install `docker-compose`.

    ```{.bash}
    DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
    mkdir -p $DOCKER_CONFIG/cli-plugins
    sudo curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o $DOCKER_CONFIG/cli-plugins/docker-compose
    sudo chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose
    docker compose version
    ```

1. Run `FMBench` with a packaged or a custom config file. **_This step will also deploy the model on the EC2 instance_**. The `--write-bucket` parameter value is just a placeholder and an actual S3 bucket is not required. You could set the `--tmp-dir` flag to an EFA path instead of `/tmp` if using a shared path for storing config files and reports.

    ```{.bash}
    fmbench --config-file /tmp/fmbench-read/configs/llama3/8b/config-ec2-llama3-8b-c5-18xlarge.yml --local-mode yes --write-bucket placeholder --tmp-dir /tmp > fmbench.log 2>&1
    ```

1. Open a new Terminal and and do a `tail` on `fmbench.log` to see a live log of the run.

    ```{.bash}
    tail -f fmbench.log
    ```

1. All metrics are stored in the `/tmp/fmbench-write` directory created automatically by the `fmbench` package. Once the run completes all files are copied locally in a `results-*` folder as usual.

## Benchmarking the Triton inference server on GPU instances

Here are the steps for using the [Triton inference server](https://github.com/triton-inference-server/server) and benchmarking model performance. The steps presented here are based on several publicly available resources such as [Deploying Hugging Face Llama2-7b Model in Triton](https://github.com/triton-inference-server/tutorials/blob/main/Popular_Models_Guide/Llama2/trtllm_guide.md), [TensorRT-LLM README](https://github.com/NVIDIA/TensorRT-LLM/blob/main/examples/llama/README.md), [End to end flow to run Llama-7b](https://github.com/triton-inference-server/tensorrtllm_backend/blob/main/docs/llama.md) and others.

1. Install the TensorRT backend.

```{.bash}
git clone https://github.com/triton-inference-server/tensorrtllm_backend.git  --branch v0.12.0
# Update the submodules
cd tensorrtllm_backend
# Install git-lfs if needed
apt-get update && apt-get install git-lfs -y --no-install-recommends
git lfs install
git submodule update --init --recursive
```

1. That's it, everything else is encapsulated within the `FMBench` code. `FMBench` would copy the relevant scripts in the `${HOME}/deploy_on_triton` directory and run `docker compose up -d` to deploy the model. Here is an example command for benchmarking `Llama3-8b-instruct` model served using Triton.

```{.bash}
fmbench --config-file /tmp/fmbench-read/configs/llama3/8b/config-ec2-llama3-8b-triton-g5.12xlarge.yml --local-mode yes --write-bucket placeholder --tmp-dir /tmp > fmbench.log 2>&1
```
