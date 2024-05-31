plugin_name=$1

source $iso_plugins_automation/config/config.sh

plugin_name_last="${plugin_name##*/}"
#echo $plugin_name_last
rm -rf $iso_plugins_automation/create_readme/package
mkdir -p $iso_plugins_automation/create_readme/package

# untar plugin tar file to package folder
tar -zxf $plugin_tar_path/$plugin_name_last/`ls $plugin_tar_path/$plugin_name_last | head -n 1` -C $iso_plugins_automation/create_readme/package
#plugin_name_without_underscore="${plugin_name//_}"


# remove underscore from json file

rm -f $iso_plugins_automation/create_readme/README.md
python3 $iso_plugins_automation/create_readme/create_readme.py $iso_plugins_automation/create_readme/package/ $iso_plugins_automation/create_readme/README.md $plugin_name_last