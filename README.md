# iso_plugins_automation

Helpful in running FSO command directly using terminal on local Machine

## SETUP STEPS :-

1. **clone this repo**.
2. **edit config/config.sh**

```
user="root"   #user name of VM
remote_ip="10.14.43.xx"   #ip-address of VM

iso_plugin_path=<> #iso-plugins project path
plugin_tar_path=<> #create a folder for storing the plugin tar file and give path of that folder
```

3. **set environment variable**

```commandline
export iso_plugins_automation=<iso_plugins_automation path>  # the path of iso_plugin_automation
```

4. **run install.sh**

```commandline
sh ./install.sh
```

5. **add alias**

```commandline
alias install_package="sh $iso_plugins_automation/install_package/install_package.sh"
alias uninstall_package="sh $iso_plugins_automation/uninstall_package/uninstall_package.sh"
alias list_installed_packages="sh $iso_plugins_automation/installed_packages/installed_packages.sh"
alias restart_fso="sh $iso_plugins_automation/restart_fso/restart_fso.sh"
alias fso_status="sh $iso_plugins_automation/fso_status/fso_status.sh"
alias unittest="sh $iso_plugins_automation/unittest/unittest.sh"
alias load_snapshot="sh $iso_plugins_automation/snapshot/load_snapshot.sh"
alias save_snapshot="sh $iso_plugins_automation/snapshot/save_snapshot.sh"
alias fso_reset="sh $iso_plugins_automation/fso_reset/fso_reset.sh"
alias reset_password="sh $iso_plugins_automation/reset_password/reset_password.sh"
alias send="sh $iso_plugins_automation/send/send.sh"
alias receive="sh $iso_plugins_automation/receive/receive.sh"
alias generate_tar="sh $iso_plugins_automation/generate_tar/generate_tar.sh"
alias create_readme="sh $iso_plugins_automation/create_readme/create_readme.sh"
alias get_log="sh $iso_plugins_automation/log/get_log.sh"
alias clear_log="sh $iso_plugins_automation/log/clear_log.sh"
```

## How to Reset FSO

- command to reset FSO

```commandline
fso_reset
```

## How to generate plugin_tar

- both sr and non-sr plugin_tar in plugin_tar file

```commandline
generate_tar <plugin_vendor>/<plugin_name>
eg. generate_tar fireeye/intel_feed
```

## How to install specific plugin

- command to install sr plugin

```commandline
install_plugin <plugin_vendor>/<plugin_name> sr
eg. install_plugin fireeye/helix sr
```

- command to install non-sr plugin

```commandline
install_plugin <plugin_vendor>/<plugin_name> non-sr
eg. install_plugin fireeye/helix non-sr
```

- command to install sr plugin forcefully if that plugin is already installed

```commandline
install_plugin <plugin_vendor>/<plugin_name> --force sr
eg. install_plugin fireeye/helix --force sr
```

- command to install non-sr plugin forcefully if that plugin is already installed

```commandline
install_plugin <plugin_vendor>/<plugin_name> --force non-sr
eg. install_plugin fireeye/helix --force non-sr
```

## List Installed Packages on FSO Machine

```commandline
list_installed_packages
```

## receive file/dir from FSO Machine to local Machine

```commandline
receive <path_on_fso> <local_path>
eg. receive /var/log/fireeye/fso/web/web.log ~/Desktop/FPLUG/FSO-2787/
```

## Reset password to login in FSO UI

```commandline
reset_password <username> <password>
```

- command to change password to default
  default username - 'fso_admin'
  default password - 'changeme'

```commandline
reset_password
```

## Restart FSO Machine

```commandline
restart_fso
```

## Send file/dir from local machine to FSO Machine

```commandline
send <local_path> <path_on_fso>
eg. send sld_data.csv /var/tmp/fso
```

## How to Load or Save Snapshot

- Load specific snapshot

```commandline
load_snapshot <path of snapshot on local machine>
load_snapshot fso_snapshot_07-26-2022_18-00-01
```

- save snapshot of FSO

```commandline
save_snapshot <snapshot_name> --include-encryted <local_path> #to save encryted snapshot
save_snapshot <snapshot_name> <local_path>  # without encryted
eg. save_snapshot helix_snapshot ~/Desktop
save_snapshot helix_snapshot (will save snapshot in current working dir on local machine)
```

- create README.md of the specific plugin

```commandline
create_readme <plugin_vendor>/<plugin_name>
eg. create_readme microsoft/smb_share
README.md file will be created in iso_plugins_automation/create_readme folder
```

## How to uninstall specific Plugin

```commandline
uninstall_package <package_name>
# use list_installed_package to list all installed packages
# will search installed packages with suffix package_name you provided and will uninstall all the packages with matching suffix
# for eg. uninstall_package helix will uninstall all the packages starting with helix
```

## How to run unit test

- command to run specific unit test

```commandline
unittest <plugin_vendor>/<plugin_name> <unit_test_name>
eg. unittest microsoft/teams CommandTest::test_testDevice
```

- command to run all unit test

```commandline
unittest <plugin_vendor>/<plugin_name>
eg. unittest microsoft/teams
```

- command to get log

```commandline
get_log
```

- command to clear log

```commandline
clear_log
```