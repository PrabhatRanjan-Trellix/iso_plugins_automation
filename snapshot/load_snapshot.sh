source $iso_plugins_automation/config/config.sh

snapshot_file=$1

rsync $snapshot_file $user@$remote_ip:/opt/fireeye/fso/snapshot/
user="ixoperator"
snapshot_file_name_last="${snapshot_file##*/}"
ssh $user@$remote_ip "cd /opt/fireeye/fso &&  bin/fso snapshot load snapshot/$snapshot_file_name_last"