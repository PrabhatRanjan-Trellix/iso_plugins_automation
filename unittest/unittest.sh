#!/bin/bash

# Source configuration and utility scripts
source "$iso_plugins_automation/config/config.sh"
source "${iso_plugins_automation}/utils/utils.sh"

# Set plugin name from the command-line argument
plugin_name="$1" # bmc/remedy

# Get the parent directory of the plugin source code
parent_dir=$(get_parent_dir "${plugins_source_code_path}/${plugin_name}")

# Create the parent directory in the Docker container
docker exec -it fso_dev bash -c "mkdir -p ${parent_dir}"

# Copy the plugin source code to the Docker container
docker cp "${saas_plugins_path}${plugin_name}" "${docker_container}:${parent_dir}/"

if [ "$2" ]; then
  docker exec -it fso_dev bash -c "\
      source /usr/python/global/bin/activate \
      && export PYTHONPATH=\"\$PYTHONPATH:\$ISO_BASE/apps/engine/python\" \
      && pytest -s \$(find ${plugins_source_code_path}/${plugin_name}/unit_test -name '*_unit_test.py')::$2"

else
  docker exec -it fso_dev bash -c "\
    source /usr/python/global/bin/activate \
    && export PYTHONPATH=\"\$PYTHONPATH:\$ISO_BASE/apps/engine/python\" \
    && pytest -s \$(find ${plugins_source_code_path}/${plugin_name}/unit_test -name '*_unit_test.py')"
fi
