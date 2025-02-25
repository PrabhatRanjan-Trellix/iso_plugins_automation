#!/bin/bash

plugin_name="$1"

source "$iso_plugins_automation/config/config.sh"
source "$iso_plugins_automation/utils/utils.sh"

if [ "$2" != "" ]; then
    plugin_tar_path="$2"
fi


# Get the parent directory of the plugin source code
parent_source_dir=$(get_parent_dir "${plugins_source_code_path}/${plugin_name}")
parent_schema_dir=$(get_parent_dir "${plugins_schema_path_docker}/${plugin_name}")
# Create the parent directory in the Docker container
docker exec -it fso_dev bash -c "mkdir -p ${parent_source_dir} && mkdir -p ${parent_schema_dir}"
# Copy the plugin source code to the Docker container
docker cp "${saas_plugins_path}${plugin_name}" "${docker_container}:${parent_source_dir}/"
docker cp "${saas_plugins_path}/categories.json" "${docker_container}:${plugin_automation_base_path}/"
docker exec -it fso_dev bash -c "\
    source /usr/python/global/bin/activate \
    && export PYTHONPATH="$PYTHONPATH:/vagrant/python"\
    && mkdir -p \"${plugins_schema_path_docker}/${plugin_name}\" \
    && cd \"${plugins_schema_path_docker}/${plugin_name}\" \
    && /vagrant/python/bin/package_plugin -f \"${plugins_source_code_path}/${plugin_name}\" -o \"${plugins_schema_path_docker}/${plugin_name}\" -p "${plugin_automation_base_path}/categories.json" 
"

parent_schema_path=$(get_parent_dir "${plugins_schema_path}/${plugin_name}")
mkdir -p ${plugins_schema_path}/${plugin_name}
docker cp "${docker_container}:${plugins_schema_path_docker}/${plugin_name}/" "${parent_schema_path}"

