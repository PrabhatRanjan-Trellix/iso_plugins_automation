plugin_name=$1

source $iso_plugins_automation/config/config.sh

if [ "$2" != "" ]; then
    plugin_tar_path=$2
fi

plugin_name_last="${plugin_name##*/}"

rsync -r $iso_plugin_path$plugin_name $user@$remote_ip:/opt/fireeye/fso/source/
ssh $user@$remote_ip "cd /opt/fireeye/fso && source config/iso_package_dev_env && rm -rvf target/$plugin_name_last && apps/engine/python/bin/package_plugin -f source/$plugin_name_last -o target/$plugin_name_last --include-deps && apps/engine/python/bin/package_plugin -f source/$plugin_name_last -o target/$plugin_name_last"
rsync -r $user@$remote_ip:/opt/fireeye/fso/target/$plugin_name_last $plugin_tar_path

