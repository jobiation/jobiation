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

##################################################################################
#############Send Commands Options###################################################
##################################################################################

save_facts = 1;
facts_module = "cisco.ios.ios_facts";
search_facts = "";

save_showcmd = 1;
showcmd = "show running-config";
search_showcmd = "GigabitEthernet0/0/0";

when_enable = 1;
when_condition = 'jobiation_facts["ansible_facts"]["ansible_net_interfaces"]["GigabitEthernet0/0/0"]["macaddress"] == "2436.daf2.dc00" and jobiation_showcmd is search("ip name-server 192.168.254.254")';

reload_in = 1; # Change this to a non-zero value to do a delayed restart of all Cisco devices included in the hosts file

##################################################################################
#############Get Output Options###################################################
##################################################################################

commands_to_remove = "";

## Define the jobs exports in the following format:
## directoryname : command
## Note that each key must be unique.
showcmd_exports = {
    # "showrun":"show running-config",
    # "showver":"show version",
    # "showint":"show int status"
    }

## Define the facts module to use for the export.
# facts_export = "cisco.ios.ios_facts";

## Define search objects
## This is optional.
## You can write your search criteria stored in variables here and then reference the variables in the searches dictionary.
## You can also not define any variables in this section and specify your search criteria in the searches dictionary.
my_search_object = "17.3.4";

## Define your searches in the following format:
## columnname : directoryname!!searchcriteria
searches = {
    ## Example search that searches the show run output for the ntp server command.
    # "has_ntp":"showrun!!ntp server 10.1.1.1",
    # "has_tacacs":"showrun!!ip tacacs server isetacacs",
    # "needs_upgrade":"showver!!"+my_search_object,
    "has8interfaces":"facts!!GigabitEthernet0/0/7"
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


