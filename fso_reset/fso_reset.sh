source $iso_plugins_automation/config/config.sh
echo "Performing a reset will destroy ALL FSO, postgres data,
The FSO service will be stopped during the process.
Are you sure you want to proceed and reset all data? [y/N]"
ssh $user@$remote_ip "cd /opt/fireeye/fso &&  bin/fso reset"