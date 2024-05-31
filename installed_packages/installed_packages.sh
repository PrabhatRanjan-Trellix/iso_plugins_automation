source $iso_plugins_automation/config/config.sh
user="ixoperator"

ssh $user@$remote_ip 'cd /opt/fireeye/fso &&  bin/fso package list'