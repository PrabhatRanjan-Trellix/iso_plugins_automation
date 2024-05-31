source $iso_plugins_automation/config/config.sh

ssh $user@$remote_ip 'systemctl status fso && systemctl status fso-web'