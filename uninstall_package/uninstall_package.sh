source $iso_plugins_automation/config/config.sh
user="ixoperator"
plugin_name=$1

package_names=$(ssh $user@$remote_ip '/opt/fireeye/fso/bin/fso package list' | grep $plugin_name | tr ">>" "\n")

oldstr=">>"
newstr=""
for package_name in $package_names
do
  package_name=$(echo $package_name | sed "s/$oldstr/$newstr/")
  ssh $user@$remote_ip "/opt/fireeye/fso/bin/fso package uninstall $package_name"
done


