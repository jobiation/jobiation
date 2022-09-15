
# # Enable service account

# Set variables
    $ansible_server = "ansible";
    $devices_file = "..\devices.csv";
    $textedit_loc = "C:\Users\me\AppData\Local\Programs\Microsoft VS Code\Code.exe";

# Copy hosts header to the ansible repo
    copy-item $devices_file "\\$ansible_server\ansiblerepo\playbooks\ansible_get_output_py"

# Copy ansible_get_output_vars.py to the ansible repo
    copy-item "ansible_get_output_vars.py" "\\$ansible_server\ansiblerepo\playbooks\ansible_get_output_py"

# Copy devices.csv to the ansible repo
    copy-item "hosts_header" "\\$ansible_server\ansiblerepo\playbooks\ansible_get_output_py"

exit;

# Create a directory for the files
    $current_time=get-date -uformat %Y%m%d_%H%M%S
    $current_dir = ".\playbooks\$current_time";
    mkdir $current_dir;

# # Run playbook an Ansible server
    plink "ansibleadmin@$ansible_server" "/var/ansiblerepo/playbooks/ansible_get_output_py/ansible_get_output_py.py"

# Copy output back to current directory
    copy-item "\\$ansible_server\ansiblerepo\playbooks\ansible_get_output\output\*" "$current_dir"

# # Disable service account
#     Set-ADUser -Identity "cn=NetcommAnsible,ou=netcomm_users,ou=netcomm,ou=oim,ou=headquarters,dc=deep,dc=state,dc=ct,dc=us" -Enabled $false;
