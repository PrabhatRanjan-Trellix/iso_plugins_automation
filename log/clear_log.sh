source $iso_plugins_automation/config/config.sh
ssh $user@$remote_ip "cat /dev/null > /var/log/fireeye/fso/web/web.log"