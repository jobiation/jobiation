#!/usr/bin/env python3
import re
import sys

# Hosts header options
ansible_python_interpreter = "/usr/bin/python3";
ansible_connection = "network_cli";
ansible_network_os = "ios";
ansible_port = "22";
ansible_user = "jobiation";
use_hosts_header = 0;
remove_hosts_header = 0;
remove_username = 0;
remove_password = 1;

# Playbook header options
gather_facts = "no";
ansible_command_timeout = "30";
connection = "local";
cisco_product_line = "ios_command";

# Send command options
when_condition = '["ansible_facts"]["ansible_net_interfaces"]["GigabitEthernet0/0/0"]["macaddress"] == "2436.daf2.dc00"';
reload_in = -1; # Change this to a non-zero value to do a delayed restart of all Cisco devices included in the hosts file

#############Get Output Options
commands_to_remove = "";

################ Input Validation
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


