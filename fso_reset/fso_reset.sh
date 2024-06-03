#!/bin/bash

# Ensure script stops on error
set -e

# Source the configuration file
source "$iso_plugins_automation/config/config.sh"


echo "Please update AWS credentials of AWS Delta 0 account before doing setup"

# Log in to AWS SSO
#aws sso login

# Log in to Docker registry
aws ecr get-login-password --region "${aws_region}" --no-verify-ssl | \
    docker login --username AWS --password-stdin "${aws_account_id}.dkr.ecr.${aws_region}.amazonaws.com"

# Remove Docker image and pull the latest
docker image rm -f "${aws_account_id}.dkr.ecr.${aws_region}.amazonaws.com/${fso_dev_image_name}:${image_tag}" && \
    docker pull "${aws_account_id}.dkr.ecr.${aws_region}.amazonaws.com/${fso_dev_image_name}:${image_tag}"

# Navigate to FSO system path, shut down existing Docker containers, and bring them up
cd "${fso_system_path}" && \
    docker-compose down && \
    docker-compose up -d