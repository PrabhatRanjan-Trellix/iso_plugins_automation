source $iso_plugins_automation/config/config.sh
user="ixoperator"

snapshot_file_name=$1
snapshot_local_path='.' # default to current dir
if [ "$2" == "--include-encrypted" ]; then
  ssh  $user@$remote_ip "cd /opt/fireeye/fso/snapshot && ../bin/fso snapshot save --include-encrypted $snapshot_file_name"
  if [ "$3" != "" ]; then
    snapshot_local_path=$3
  fi
else
  ssh  $user@$remote_ip "cd /opt/fireeye/fso/snapshot && ../bin/fso snapshot save $snapshot_file_name"
  if [ "$2" != "" ]; then
    snapshot_local_path=$2
  fi
fi

user="root"
rsync $user@$remote_ip:/opt/fireeye/fso/snapshot/$snapshot_file_name $snapshot_local_path