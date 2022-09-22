#!/usr/bin/env python3
import re
import sys

# Host file options
ansible_python_interpreter = "/usr/bin/python3";
ansible_connection = "network_cli";
ansible_network_os = "ios";
ansible_port = "22";
ansible_user = "me";
root_dir = "";


# If this options is set to 1, then root_dir/common/hosts_header must exist.
use_hosts_header = 0; 

# Valid input: 1 or 0.
# Saves the username in the jobs archive hosts file
save_username = 1;

add_when_condition = 0;

hosts_conditions_prompt = 1; # 1 is prompt the user to look at the hosts conditions file, 0 is not.
prompt_for_write = 1; # 1 means the user will be prompted to do a write before the playbook starts
prompt_for_reload = 1; # 1 means the user will be prompted to do a reload and for the seconds

prompt_for_search_criteria = 1; # Asks the users if they completed the search_criteria.txt
commands_to_remove = "adCf7 8jjd";
output_retention = 30; # Specify the number of days

output_dir = "/var/ansiblerepo/5scripts";
ansible_dir = "/etc/ansible";

################
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


