#!/usr/bin/env python3

#    Copyright 2023 Anthony Tranquillo

#    This file is part of Jobiation.

#    Jobiation is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

#    Jobiation is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License along with Jobiation.  If not, see <http://www.gnu.org/licenses/>.

#####################################################################################
#############Global Options##########################################################
#####################################################################################

### Hosts file options
ansible_python_interpreter = "/usr/bin/python3";
ansible_connection = "network_cli";
ansible_network_os = "ios";
ansible_port = 22;

use_hosts_header = False;
hosts_header = "../hosts_header"; # Location of the hosts_header file relative to the scripts. For example the path relative to get_output.py
ansible_user = "";

### Location of ansible-playbook executable
ansible_exe = "/usr/bin/ansible-playbook"; # For when Ansible is installed for the whole system. 
# ansible_exe = "/home/username/.local/bin/ansible-playbook"; # For when Ansible is installed for a single user

remove_hosts_header = False;
remove_become = True; # Only works if using hosts_header; ansible_username: must come directly after ansible_become_password: . 
remove_username = False; # Only works if using hosts_header; ansible_password: must come directly after ansible_username. 
remove_password = True; # Only works if using hosts_header; children: must come directly after ansible_password:
inventory_file = "../inventory.csv"; # Location of the inventory file relative to the scripts. For example the path relative to get_output.py
convert_host_line_end = False; # converts the host file line endings to CRLF

### Playbook header options
gather_facts = "no";
ansible_command_timeout = 30;
cisco_command_type = "cisco.ios.ios_command"; # Note that in some versions you do not write the full path. For example, instead of 'cisco.ios.ios_commands' you would just write 'ios_commands'
convert_pb_line_end = False; # converts the playbook file line endings to CRLF

### Location of the host_conditions file relative to the scripts, such as send_commands.py.
host_conditions_file = "../host_conditions.py";

### prepend_job_name is a string you want prepended to the names of directories that hold job results.
### Leave the value of prepend_job_name equal to empty quotes to prepend nothing.
prepend_job_name = "";

### Uncomment the revert_timer and archive_path variable to revert back to the previous config should any commands fail.
### Uncomment the config_confirm variable and set it to True to automatically confirm the config, should all the previous commands be successful.
### Revert_timer value should be an integer between 1 and 120
### Not all Cisco devices support this feature
### These options are used with send_commands, manage_acls, and upgrade_devices only
# revert_timer = 10;
# archive_path = "path flash:"; # The value can be an empty set of quotes if you already have an archive path set
# config_confirm = True;

### Uncomment notify_script, notify_recipients, and notify_subjects to enable notifications
### Please keep the message alphanumeric.
### Recipients will only be notified if there is a failure.
# notify_script = "../notification/notify.sh";
# notify_recipients = "jobiation8675309@gmail.com";
# notify_subject = "Jobiation task fail.";

#####################################################################################
#############Send Commands Options###################################################
#####################################################################################

### Uncomment the sc_reload_in variable to begin your playbook with the write command and then the reload command.
### Set sc_reload_in to the number of minutes you want to delay the reload. Must be at least 1.
# sc_reload_in = 10;

### Specify the file that holds the commands to send.
commands_file = "commands.txt";

### Uncomment and set a value for sc_facts_output to save facts from remote devices.
### In when condition statements you can reference the the facts output as 'facts_output'
### Note that in some versions you do not write the full path. For example, instead of 'cisco.ios.ios_facts' you would just write 'ios_facts'
# sc_facts_output = "cisco.ios.ios_facts";

### Uncomment the showcmd variable and specify a show command that's output you want to register.
### In when condition statements you can reference the show command's output as 'showcmd.stdout[0]'
# showcmd = "show license usage";

### Uncomment the when_conditon variable and specify a when statement
### Example: when_condition = 'facts_output["ansible_facts"]["ansible_net_model"] == "C1111-8P" and showcmd.stdout[0] is search("securityk9")';
# when_condition = '';

##################################################################################
#############Get Output Options###################################################
##################################################################################

### Define the job exports in the following format:
### directoryname : command
### Note that each key must be unique.
### You can comment out individual key:value pairs, but do not comment out the whole showcmd_exports dictionary
### Make sure to leave off the trailing comma on the last item in the dictionary.
### Keep the keys alphanumeric with underscores and less than 15 characters. First character should be a lower case letter.
showcmd_exports = {
    # "dirflash":"dir",
    # "showver":"show version",
    # "showrun":"show running-config"
};

### If you want to export facts, uncomment go_facts_output and define the facts module to use for the export.
### Note that in some versions you do not write the full path. For example, instead of 'cisco.ios.ios_facts' you would just write 'ios_facts'
# go_facts_output = "cisco.ios.ios_facts";

### If there are commands you would rather not store for security reasons, add them to the commands_to_remove dictionary.
### Use the format "directoryname":"command_1!!command_2!!command_3,"
### You can comment out individual key:value pairs, but do not comment out the whole commands_to_remove dictionary
### Make sure to leave off the trailing comma on the last item in the dictionary.
### All dictionary keys must match a key in the showcmd_exports dictionary.
### Keep the keys alphanumeric with underscores and less than 15 characters. First character should be a lower case letter.
commands_to_remove = {
    # "showrun":"enable secret!!username!!pre-shared-key",
    # "showver":"Processor board ID"
};


#####################################################################################
#############Search Output Options###################################################
#####################################################################################

### Define your searches in the following format:
### columnname : directoryname!!file extension!!searchcriteria
### You can comment out individual exports but do not comment out the whole searches dictionary
### Make sure to leave off the trailing comma on the last item in the list.
### Keep the keys alphanumeric with underscores and less than 15 characters. First character should be a lower case letter.
searches = {
    # "has_8interfaces":"showrun!!.txt!!interface GigabitEthernet0/1/7",
    # "has17_6_3":"dirflash!!.txt!!706422748(.*)c1100-universalk9.17.06.03a.SPA.bin"
    # "peer1111" : "showrun!!.txt!!tunnel destination 1.1.1.1",
    # "is8p" : "facts!!.json!!ansible_net_model\" :\"C1111-8P"
};

##################################################################################
#############Manage ACLs###########################################################
##################################################################################

### Uncomment the ma_reload_in variable to begin your playbook with the write command and then the reload command.
### If your commands are successful, then run a send_commands job to write the changes and cancel the reload.
### Set ma_reload_in to the number of minutes you want to delay the reload. Must be at least 1.
# ma_reload_in = 10;

### Set the ma_write variable to True to end the batch of commands with the write command
ma_write = True;

### Define your ACL groups in the following format:
### "aclgroup":"friendlyname_for_acl",
### "declaration":"the_line_that_creates_the_acl",
### "interfaces":"interface1,interface2,interface3", # Specify a comma separated list of interfaces if more than one.
### "application":"the_line_that_applies_the_acl_to_an_interface",
### "lastline":"last_line_of_acl"
### You can comment out individual key:value pairs but do not comment out the whole aCLs dictionary
### Make sure to leave off the trailing comma on the last item in the dictionary.
### Keep the keys alphanumeric with underscores and less than 15 characters. First character should be a lower case letter.

aCLs = {

### Interface ACL Example:
# "aclgroup":"exampleACL",
# "declaration":"ip access-list extended exampleACL",
# "interfaces":"gi0/0/0", # Specify a comma separated list of interfaces if more than one.
# "application":"ip access-group exampleACL in",
# "lastline":"deny ip any any"

### Interface ACL Example with variables:
# "aclgroup":"exampleACL",
# "declaration":"ip access-list extended exampleACL",
# "interfaces":"!interface1!,!interface2!", # Specify a comma separated list of interfaces if more than one.
# "application":"ip access-group exampleACL !direction!",
# "lastline":"!lastline!"

# ### VTY ACL Example
# "name":"vtyACL",
# "declaration":"ip access-list standard vtyACL",
# "interfaces":"line vty 0 4, line vty 5 15", # Specify a comma separated list of interfaces if more than one.
# "application":"ip access-class vtyACL in",
# "lastline":"deny ip any any log"

}

##################################################################################
#############Upgrade Devices######################################################
##################################################################################

### Specify the module for gathering facts
ud_facts_output = "cisco.ios.ios_facts";

### Set the ud_file_copy variable to True if you want to copy the image specified in the new_image_file variable.
ud_file_copy = True;

### Set the ud_boot_sys_cmd variable to True if you want to add the boot system command specified in new_boot_cmd.
### This will also add a boot system command for the image to which your router is currently booted after the new_boot_cmd.
ud_boot_sys_cmd = True;

### Set the ud_write option to True to save the changes made when ud_boot_sys_cmd is enabled.
ud_write = True; # No need to use with ud_reload

### Uncomment the ud_reload_in variable to end your playbook with the write command and then the reload command.
### Set sc_reload_in variable to the number of minutes you want to delay the reload. Must be at least 1.
# ud_reload_in = 10;

### The new_image_file is the name of the image file to which you want to upgrade
### It is best not to change Cisco's name for the image. It could cause the duplicate image check to fail.
new_image_file = "c1100-universalk9.17.06.03a.SPA.bin"

### The copy_file_cmd is the command you would type to copy the file to your device.
### http is recommended but tftp works too.
copy_file_cmd = "copy http://192.168.254.209/" + new_image_file + " flash:";

### The new_boot_cmd is the command you would type to tell your device where to find the new image.
new_boot_cmd = "boot system flash:/" + new_image_file;

### The old_image_file variable is the location of the image from which your device booted, retrieved from ansible_facts output.
old_image_file = "[\\'ansible_facts\\'][\\'ansible_net_image\\']";

### The space required should be set to the size of the image to which you are upgrading in kilobytes, plus any free space you would like to have.
space_required = 706422+10000;

### The free_space variable is amount of free space in flash memory retrieved from ansible_facts output.
free_space = "[\\'ansible_facts\\'][\\'ansible_net_filesystems_info\\'][\\'bootflash:\\'][\\'spacefree_kb\\']";

### The config_register value desired.
config_register = "0x2102";

### The falue of the prompt the device will give when copying the file name. It can be abbreviated to just the first part of the prompt.
filename_prompt = "Destination filename";