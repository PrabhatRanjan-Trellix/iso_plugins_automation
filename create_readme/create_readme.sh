plugin_name=$1

source $iso_plugins_automation/config/config.sh

rm -rf $iso_plugins_automation/create_readme/package
mkdir -p $iso_plugins_automation/create_readme/package
sh $iso_plugins_automation/generate_tar/generate_tar.sh $plugin_name
# untar plugin tar file to package folder
tar -zxf $plugins_tar_path/$plugin_name/`ls $plugins_tar_path/$plugin_name | head -n 1` -C $iso_plugins_automation/create_readme/package
#plugin_name_without_underscore="${plugin_name//_}"


# remove underscore from json file

rm -f $iso_plugins_automation/create_readme/README.md
python3 $iso_plugins_automation/create_readme/create_readme.py $iso_plugins_automation/create_readme/package/ $iso_plugins_automation/create_readme/README.md $plugin_name