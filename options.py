#!/usr/bin/env python3
import re
import sys

#####################################################################################
#############Global Options##########################################################
#####################################################################################

# Hosts file options
ansible_python_interpreter = "/usr/bin/python3";
ansible_connection = "network_cli";
ansible_network_os = "ios";
ansible_port = 22;
ansible_user = "jobiation";
use_hosts_header = True;
remove_hosts_header = False;
remove_username = False;
remove_password = False;

# Playbook header options
gather_facts = "no";
ansible_command_timeout = 30;
cisco_product_line = "cisco.ios.ios_command";

### Uncomment the reload_in variable to begin your playbook with the write and reload commands.
### Uncommenting reload_in will also omit the write command at the end so your changes will not be saved.
### Use this option if you think there is a small change your changes could lock you out of your devices, for example if you are editing a vty ACL.
### If your commands see successful then use the send_commands script to  write the changes.
### Set reload_in to 0 if you want to reload immediately or set reload_in to the number of minutes you want to delay the reload.
### This option is used only with send_commands and manage_acls.
# reload_in = 60;

#####################################################################################
#############Send Commands Options###################################################
#####################################################################################

### Uncomment and set a value for facts_module to save facts from remote devices.
### In when condition statements you can reference the the facts output as 'factsoutput'
#facts_module = "cisco.ios.ios_facts";

### Uncomment showcmd and specify a show command that's output you want to register.
### In when condition statements you can reference the show command's output as 'showcmd'
#showcmd = "show running-config";

### Uncomment when_conditon ans specify a when statement you wish to
### Example when condition
#when_condition = 'factsoutput["ansible_facts"]["ansible_net_interfaces"]["GigabitEthernet0/0/0"]["macaddress"] == "2436.daf2.dc00" and showcmd is search("ip name-server 192.168.254.254")';

##################################################################################
#############Get Output Options###################################################
##################################################################################

### Define the job exports in the following format:
### directoryname : command
### Note that each key must be unique.
### You can comment out individual exports but do not comment out the whole showcmd_exports dictionary
### Make sure to leave off the trailing comma on the last item in the list.
### Keep the keys alphanumeric and under 15 characters. First character should be a lower case letter.
showcmd_exports = {
    "sh8W_run_":"show running-config"
    # "show_ver":"show version"
    # "showint":"show int status"
    };

### If you wish to export facts, uncomment facts_export and define the facts module to use for the export.
# facts_export = "cisco.ios.ios_facts";

### If there are commands you would rather not store for security reasons, add them to the commands_to_remove list.
### Use the format "directoryname":"command_1!!command_2!!command_3,"
### You can comment out individual exports but do not comment out the whole commands_to_remove dictionary
### Make sure to leave off the trailing comma on the last item in the list.
### All dictionary keys must match a key in the showcmd_exports dictionary.
commands_to_remove = {
  "sh8W_run_":"enable secret!!username!!pre-shared-key"
  # "show_ver":"Configuration (.*)0x2102$"
};

#####################################################################################
#############Search Output Options###################################################
#####################################################################################

### Define search objects. This is optional.
### You can write your search criteria stored in variables here and then reference the variables in the searches dictionary.
### You can also not define any variables in this section and specify your search criteria in the searches dictionary.
my_search_object = "17.3.4";

### Define your searches in the following format:
### columnname : directoryname!!searchcriteria
### You can comment out individual exports but do not comment out the whole searches dictionary
### Make sure to leave off the trailing comma on the last item in the list.
### Keep the keys alphanumeric and under 15 characters.
searches = {
    "has_ntp":"sh8W_run_!!ip address 192.168.254.",
    "has_tacacs":"sh8W_run_!!ip tacacs server isetacacs",
    "has8interfaces":"sh8W_run_!!interface GigabitEthernet0/1/7"
    # "needs_upgrade":"showver!!"+my_search_object,
    };


##################################################################################
#############Manage ACL##########################################################
##################################################################################

### Define your ACL groups in the following format:
### "aclgroup":"friendlyname_for_acl",
### "declaration":"the_line_that_creates_the_acl",
### "interfaces":"interface,interface,interface", # Specify a comma separated list of interfaces if more than one.
### "application":"the_line_that_applies_the_acl_to_an_interface",
### "lastline":"last_line_of_acl"
### You can comment out individual exports but do not comment out the whole aCLs dictionary
### Make sure to leave off the trailing comma on the last item in the list.
### Keep the keys alphanumeric and under 15 characters.

aCLs = {

# ##### Tunnel ACLs
"aclgroup":"tunnelACL",
"declaration":"ip access-list extended TunnelACL",
"interfaces":"interface g0/0/0,interface TunnelACL 100", # Specify a comma separated list of interfaces if more than one.
"application":"ip access-group TunnelACL !TunnelACL_dir!",
"lastline":"deny ip any any log"

# ##### VTY ACl Example
# "name":"vtyACL",
# "declaration":"ip access-list standard VTYACL",
# "interfaces":"line vty 0 4, line vty 5 15", # Specify a comma separated list of interfaces if more than one.
# "application":"ip access-class VTYACL in",
# "lastline":"deny ip any any"

}

##################################################################################
#############Input Validation#####################################################
##################################################################################

# boolreg =re.compile("^[0-1]$");
# numericreg =re.compile("^[0-9]$");
# alphanumericreg =re.compile("^([0-9]?[a-z]?[A-Z]?){1,20}$");

# remove_username_match = re.search(boolreg, str(remove_username))
# if not remove_username_match:
#   print("remove_username variable invalid. Change value in options.py.");
#   sys.exit();

# use_hosts_header_match = re.search(boolreg, str(use_hosts_header))
# if not use_hosts_header_match:
#   print("use_hosts_header variable invalid. Change value in options.py.");
#   sys.exit();
