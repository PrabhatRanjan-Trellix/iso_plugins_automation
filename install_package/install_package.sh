source $iso_plugins_automation/config/config.sh
user="ixoperator"

if [ -f $1 ]; then
  rsync $1 root@$remote_ip:/opt/fireeye/fso/target/
  plugin_tar_filename="${1##*/}"
  echo $plugin_tar_filename
  ssh $user@$remote_ip "cd /opt/fireeye/fso &&  bin/fso package install --force-reinstall target/$plugin_tar_filename"
#  ssh
else
  plugin_name=$1
  plugin_last_name="${plugin_name##*/}"

  sh $iso_plugins_automation/generate_tar/generate_tar.sh $1

  if [ "$2" == "--force" ]; then
    if [ "$3" == "sr" ]; then
      ssh $user@$remote_ip "cd /opt/fireeye/fso &&  bin/fso package install --force-reinstall target/$plugin_last_name/${target/$plugin_last_name | head -1}"
    else
      ssh $user@$remote_ip "cd /opt/fireeye/fso &&  bin/fso package install --force-reinstall target/$plugin_last_name/${target/$plugin_last_name | tail -n1}"
    fi
  else
    if [ "$2" == "sr" ]; then
      ssh $user@$remote_ip "cd /opt/fireeye/fso &&  bin/fso package install target/$plugin_last_name/${target/$plugin_last_name | head -1}"
    else
      ssh $user@$remote_ip "cd /opt/fireeye/fso &&  bin/fso package install target/$plugin_last_name/${target/$plugin_last_name | tail -n1}"
    fi
  fi
fi