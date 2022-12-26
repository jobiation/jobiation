#!/usr/bin/env python3
import re
import sys

# Hosts file options
ansible_python_interpreter = "/usr/bin/python3";
ansible_connection = "network_cli";
ansible_network_os = "ios";
ansible_port = "22";
ansible_user = "jobiation";
use_hosts_header = 1;
remove_hosts_header = 0;
remove_username = 0;
remove_password = 0;

# Playbook header options
gather_facts = "no";
ansible_command_timeout = "30";
cisco_product_line = "cisco.ios.ios_command";

# reload_in = 60; # This option is used with send_commands and manage_acls.

##################################################################################
#############Send Commands Options###################################################
##################################################################################

### Uncomment and set a value for facts_module to save facts from remote devices.
### In when condition statements you can reference the the facts output as 'factsoutput'
#facts_module = "cisco.ios.ios_facts";

### Uncomment showcmd and specify a show command that's output you want to register.
### In when condition statements you can reference the show cammand's output as 'showcmd'
#showcmd = "show running-config";

### Uncomment when_conditon ans specify a when statement you wish to 
#when_condition = 'factsoutput["ansible_facts"]["ansible_net_interfaces"]["GigabitEthernet0/0/0"]["macaddress"] == "2436.daf2.dc00" and showcmd is search("ip name-server 192.168.254.254")';

### Uncomment the reload_in variable to begin your playbook with a write and reload command.
### Set reload_in to 0 if you want to reload immediately or set reload_in to the number of minutes you want to delay the reload.

##################################################################################
#############Get Output Options###################################################
##################################################################################

### If there are commands you would rather not store for security reasons, add them to the commands_to_remove list.
### Make sure to leave off the trailing comma on the last item in the list.
commands_to_remove = {
  "showrun":"enable secret!!username!!flash(.*).bin",
  "showver":"Configuration (.*)0x2102$!!10 Gigabit Ethernet interfaces"
};

## Define the jobs exports in the following format:
## directoryname : command
## Note that each key must be unique.
### You can comment out individual exports but do not comment out the whole showcmd_exports dictionary
showcmd_exports = {
    "showrun":"show running-config",
    "showver":"show version"
    # "showint":"show int status"
    };

## If you wish to export facts, uncomment facts_export and define the facts module to use for the export.
facts_export = "cisco.ios.ios_facts";

##################################################################################
#############Search Output Options###################################################
##################################################################################

## Define search objects
## This is optional.
## You can write your search criteria stored in variables here and then reference the variables in the searches dictionary.
## You can also not define any variables in this section and specify your search criteria in the searches dictionary.
my_search_object = "17.6.3";

## Define your searches in the following format:
## columnname : directoryname!!searchcriteria
# You can comment out searches but do not comment out the whole searches dictionary.
searches = {
    ## Example search that searches the show run output for the ntp server command.
    # "has_ntp":"showrun!!ntp server 10.1.1.1",
    # "has_tacacs":"showrun!!ip tacacs server isetacacs",
    "needs_upgrade":"showver!!"+my_search_object,
    "has8interfaces":"showrun!!interface GigabitEthernet0/0/0(.*\n){1,4}interface GigabitEthernet0/0/1"
    };


##################################################################################
#############Manage ACL###################################################
##################################################################################

# Single managed ACLs

aCLs = {

##### Tunnel ACLs
"aclgroup":"TACL", #1 or 0
"declaration":"ip access-list extended TunnelACL",
"interfaces":"interface g0/0/0,interface TunnelACL 100",
"application":"ip access-group TunnelACL in",
"preadd":"!TACL_pa", # 1 or 0 - Important to include the name of the acl in the column in case more than one
"postadd":"!TACL_pa", # 1 or 0 - Important to include the name of the acl in the column in case more than one
"lastline":"deny ip any any log" # Can be column name or literal

# ##### VTY ACl Example
# "name":"VTYACL",
# "declaration":"ip access-list standard VTYACL",
# "interfaces":"line vty 0 4, line vty 5 15",
# "application":"ip access-class VTYACL in",
# "preadd":"!preaddcol",
# "postadd":"!postaddcol",
# "lastline":"deny ip any any"

}

##################################################################################
#############Input Validation#####################################################
##################################################################################

boolreg =re.compile("^[0-1]$");
numericreg =re.compile("^[0-9]$");
alphanumericreg =re.compile("^([0-9]?[a-z]?[A-Z]?){1,20}$");

remove_username_match = re.search(boolreg, str(remove_username))
if not remove_username_match:
  print("remove_username variable invalid. Change value in options.py.");
  sys.exit();

use_hosts_header_match = re.search(boolreg, str(use_hosts_header))
if not use_hosts_header_match:
  print("use_hosts_header variable invalid. Change value in options.py.");
  sys.exit();

# commands_to_remove_match = re.search(alphanumericreg, str(commands_to_remove))
# if commands_to_remove_match:
#     print("Match");
# else:
#     print("No match");


