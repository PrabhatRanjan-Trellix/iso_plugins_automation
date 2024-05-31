source $iso_plugins_automation/config/config.sh
ssh root@$remote_ip "tail -f /var/log/fireeye/fso/web/web.log"