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

# Playbook header options
gather_facts = "no";
ansible_command_timeout = "30";
connection = "local";
cisco_product_line = "ios_command";

save_username = 1;

add_when_condition = 0;

reload_in = 60; # Change this to a non-zero value to do a delayed restart of all Cisco devices included in the hosts file

commands_to_remove = "adCf7 8jjd";



################ Input Validation
boolreg =re.compile("^[0-1]$");
numericreg =re.compile("^[0-9]$");
alphanumericreg =re.compile("^([0-9]?[a-z]?[A-Z]?){1,20}$");

save_username_match = re.search(boolreg, str(save_username))
if not save_username_match:
  print("save_username variable invalid. Change value in options.py.");
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


