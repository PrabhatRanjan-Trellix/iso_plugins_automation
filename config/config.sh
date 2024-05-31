docker_container="fso_dev"
aws_account_id="185869774838"   # aws account id that contains the fso dev images in the erc
aws_region="us-west-2" # aws ecr region
fso_dev_image_name="xdr-fso-image" # fso dev image name
image_tag="6.0.0"   # fso dev image tag
plugin_automation_base_path="/root/plugins_automation"  #base path in docker container that will contain plugin command, plugin tar file
plugins_source_code_path="${plugin_automation_base_path}/source" # path contains plugins source code
plugins_target_path="${plugin_automation_base_path}/target" # path contains plugins tar file generated
plugins_schema_path_docker="${plugin_automation_base_path}/schema" # path contains schema file generated

saas_plugins_path="/Users/prabhat.ranjan/Desktop/Projects/xdr-soarcontent-iso-plugins-saas/" #iso-plugins project path in local
plugins_tar_path="/Users/prabhat.ranjan/Desktop/Projects/saas_plugins_tar" #folder store tar package of plugin in local
plugins_schema_path="/Users/prabhat.ranjan/Desktop/Projects/plugins_schema"
fso_system_path="/Users/prabhat.ranjan/Desktop/Projects/xdr-soar-fso-system"