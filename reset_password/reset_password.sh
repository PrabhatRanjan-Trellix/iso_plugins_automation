source $iso_plugins_automation/config/config.sh
user="ixoperator"

if [ "$1" == "" ]; then
  fso_user="fso_admin"
else
  fso_user=$1
fi

if [ "$2" == "" ]; then
  password="changeme"
else
  password=$2
fi

ssh $user@$remote_ip "cd /opt/fireeye/fso &&  bin/fso reset password -u $fso_user --password $password --no-check"