source $iso_plugins_automation/config/config.sh

ID_FILE="${HOME}/.ssh/id_rsa.pub"

if [ -e $ID_FILE ]; then
  echo "$ID_FILE already exist. copying to machine $remote_ip"
else
  echo "$ID_FILE not exist.creating id_rsa.pub file in ${HOME}/.ssh dir"
  ssh-keygen -t rsa
fi

ssh-copy-id -i $ID_FILE root@$remote_ip
ssh-copy-id -i $ID_FILE ixoperator@$remote_ip

echo "Successfully configured SSH Key-Based Authentication on remote machine with ip $remote_ip"

ssh $user@$remote_ip 'cd /opt/fireeye/fso && mkdir source;mkdir target;mkdir snapshot;setfacl -m u:ixoperator:rwx snapshot'

