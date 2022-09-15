#!/usr/bin/env python3

# Host file options
ansible_python_interpreter = "/usr/bin/python3";
ansible_connection = "network_cli";
ansible_network_os = "ios";
ansible_port = "22";
ansible_user = "me";
use_hosts_header = 1; # If this options is set to 1, then root_dir/common/hosts_header must exist.
output_retention = 30; # Specify the number of days
shebang = "#!/usr/bin/env python3";
save_username = 1; #Saves the username in the jobs archive hosts file
variables_used = "all"; # Option 1: all (least efficient but you can use any column as a variable), Option 2: specify a string of column names. For example, arg1,  
root_dir = "";
ansible_vault_creds = "";
save_facts = "0"; # 1 or 0 for yes or no
column_to_mark = "mrk"; # This specifies the column to mark when a conditions is searched for in the output from the get_output module
hosts_conditions_prompt = 1; # 1 is prompt the user to look at the hosts conditions file, 2 is not.
prompt_for_write = 1; # 1 means the user will be prompted to do a write before the playbook starts
prompt_for_reload = 1; # 1 means the user will be prompted to do a reload and for the seconds
prompt_for_search_criteria = 1; # Asks the users if they completed the search_criteria.txt
commands_to_remove = "enable|username";


# Output

output_dir = "/var/ansiblerepo/5scripts";

ansible_dir = "/etc/ansible";

