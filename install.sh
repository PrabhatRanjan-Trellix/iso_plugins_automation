#!/bin/bash

# Ensure script stops on error
set -e

# Source the configuration file
source "$iso_plugins_automation/config/config.sh"


echo "Please update AWS credentials of AWS Delta 0 account before doing setup"

# Log in to AWS SSO
aws sso login

# Log in to Docker registry
aws ecr get-login-password --region "${aws_region}" --no-verify-ssl | \
    docker login --username AWS --password-stdin "${aws_account_id}.dkr.ecr.${aws_region}.amazonaws.com"

# Remove Docker image and pull the latest
docker image rm -f "${aws_account_id}.dkr.ecr.${aws_region}.amazonaws.com/${fso_dev_image_name}:${image_tag}" && \
    docker pull "${aws_account_id}.dkr.ecr.${aws_region}.amazonaws.com/${fso_dev_image_name}:${image_tag}"

# create plugins_tar path and schema path if not exist in local
mkdir -p "${plugins_tar_path}"
mkdir -p "${plugins_schema_path}"

# Navigate to FSO system path, shut down existing Docker containers, and bring them up
cd "${fso_system_path}" && \
    docker-compose down && \
    docker-compose up -d

# Create directories in the Docker container
docker exec -it "${docker_container}" bash -c "\
    mkdir -p '${plugin_automation_base_path}' && \
    mkdir -p '${plugins_source_code_path}' && \
    mkdir -p '${plugins_target_path}' && \
    mkdir -p '${plugins_schema_path_docker}'"\

# Run the fso UI server
docker exec -it "${docker_container}" bash -c "\
    chmod 777 /vagrant/setup/nn.sh && \
    sh /vagrant/setup/nn.sh && \
    dnf -y install procps"

# Install pytest for unit_test
docker exec -it "${docker_container}" bash -c "\
    source /usr/python/global/bin/activate && \
    export PYTHONPATH=\"\$PYTHONPATH:\$ISO_BASE/apps/engine/python\" && \
    pip install pytest"

# start httpd server
docker exec -d "${docker_container}" bash -c "httpd -D FOREGROUND"

# Run the fso api server
docker exec -it "${docker_container}" bash -c "\
    chmod 777 /vagrant/setup/dev_init.sh && \
    sh /vagrant/setup/dev_init.sh"

