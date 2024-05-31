source $iso_plugins_automation/config/config.sh
plugin_name=$1           # bmc/remedy
plugin_name_last="${plugin_name##*/}"  #remedy

rsync -r $iso_plugin_path$plugin_name $user@$remote_ip:/opt/fireeye/fso/source/


unit_test_file=$(ssh $user@$remote_ip "cd /opt/fireeye/fso && ls source/$plugin_name_last/unit_test | grep unit_test.py")
echo $unit_test_file
# 2nd arg test_name
if [ "$unit_test_file" = "" ]
then 
    echo "unit_test_file not found"
else
    if [ $2 ];then
      ssh $user@$remote_ip "cd /opt/fireeye/fso && source config/iso_package_dev_env && pytest -s source/$plugin_name_last/unit_test/$unit_test_file::$2"
    else
      ssh $user@$remote_ip "cd /opt/fireeye/fso && source config/iso_package_dev_env && pytest -s source/$plugin_name_last/unit_test/$unit_test_file"
    fi
fi  
