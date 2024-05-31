source $iso_plugins_automation/config/config.sh

ssh $user@$remote_ip 'systemctl restart fso && systemctl restart fso-web'