source $iso_plugins_automation/config/config.sh

if [[ -d $1 ]]; then
  rsync -r $1 $user@$remote_ip:$2
elif [[ -f $1 ]]; then
  rsync $1 $user@$remote_ip:$2
else
  echo "$1 is not valid file or dir"
  exit 1
fi

