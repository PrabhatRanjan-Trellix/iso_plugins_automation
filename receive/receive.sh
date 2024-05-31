source $iso_plugins_automation/config/config.sh

rsync -r $user@$remote_ip:$1 $2