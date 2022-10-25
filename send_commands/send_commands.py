#!/usr/bin/env python3

# Imports
import csv
import sys # For exiting the script early with sys.exit();
import shutil # For copyfile
import os # For mkdir
from datetime import datetime
import subprocess # For running a bash script
import re

# Make array of required columns
req_columns = [ "devicename", "ip", "active" ];

# Import options file
sys.path.insert(1, '../');
import options

# Import send_command_functions
import scfunctions

# Get current date and time
now = datetime.now() # current date and time
date_time = now.strftime("%Y%m%d_%H%M");

# # Make a directory for the job
os.mkdir('jobs/' + date_time);
current_dir = "jobs/" + date_time;

# Copy hosts_header or check if username is needed in the options file
password_prompt = " -k";

if(options.use_hosts_header == 1):
    if not os.path.exists("../hosts_header"):
        input("You need to put a hosts_header file in the jobiation root when you set the use_hosts_header to 1 in options.py.");
        sys.exit();
    shutil.copyfile("../hosts_header", current_dir + "/hosts");
    username = "NA";
    password_prompt = "";
elif(options.ansible_user == ""):
    username = input("You do not have a username set. What username do you want to use? ");
else:
    username = options.ansible_user;

# Ask user if they want to do a write and reload
if options.reload_in >= 1:
    confirm_reload = input("ATTENTION! You have the reload_in option set to a non-zero value.\n\nYour specified devices will be reloaded in " + str(options.reload_in) + " minutes.\n\nType 'yes' if you want to continue. ");
    if confirm_reload.lower() != "yes":
        print("Aborting!");
        sys.exit();

# Open commands.txt and cache in variable commands_content
with open('commands.txt', 'r') as commands_file:
    commands_content = commands_file.read();

# open inventory.csv
inventoryfile = open("../inventory.csv","r");

# Make a list of the first line
with inventoryfile as invrow:
    firstline = invrow.readline()
flList = firstline.split(",");

# Close the inventory file
inventoryfile.close();

# Make flag variable for replacements
replacements_required = 0;

# Increment replacements_required variable and also validate the first line.
flAllowedChars =re.compile("^([0-9]?[a-z]?[A-Z]?_?){1,15}$");
for flCol in range(len(flList)-1):
    if re.search("!"+flList[flCol], commands_content):
        replacements_required = replacements_required+1;
    if not re.search(flAllowedChars, str(flList[flCol])):
        print(flList[flCol] + " contains an illegal character.\n\nThe top line of the inventory can contain numbers, letters, and underscores.\n\nAlso, please do not use more than 15 characters in any one column header.");
        sys.exit();

# Make spaces variable
if replacements_required == 0:
    spaces = "";
else:
    spaces = "        ";

# Build Hosts header if use_hosts_header == 0
if(options.use_hosts_header == 0):
    hostsfile = open(current_dir+"/hosts","w");
    hostsfile.write("---\n");
    hostsfile.write("all:\n");   
    hostsfile.write(" vars:\n");
    hostsfile.write("  ansible_python_interpreter: " + options.ansible_python_interpreter + "\n");
    hostsfile.write("  ansible_connection: " + options.ansible_connection + "\n");
    hostsfile.write("  ansible_network_os: " + options.ansible_network_os + "\n");
    hostsfile.write("  ansible_port: " + options.ansible_port + "\n");
    hostsfile.write("  ansible_user: " + username + "\n");
    hostsfile.write(" children:\n");
    hostsfile.write("   jobiation_inventory:\n");
    hostsfile.write("     hosts:\n");
    hostsfile.close();

# Make temp python file
tempfile = open("tmp/tempfile.py","w");

# Add shebang and imports to tempfile.py
tempfile.write("#!/usr/bin/env python3\n");
tempfile.write("import csv\n");
tempfile.write("import sys\n");
tempfile.write("import shutil\n");
tempfile.write("import os\n");

# Open files in tempfile.py
tempfile.write("hostsfile = open('" + current_dir + "/hosts', 'a+');\n");
tempfile.write("inventoryfile = open('../inventory.csv', 'r');\n");
tempfile.write("commandsfile = open('commands.txt', 'r');\n");
tempfile.write("playbookfile = open('" + current_dir + "/jobiation_task.yaml', 'w');\n");
tempfile.write("playbookfile.write('---\\n');\n");

# Write to playbook file in tempfile.py if replacements required
if(replacements_required == 0):
    tempfile.write("playbookfile.write('- name: jobiation_pb\\n');\n");
    tempfile.write("playbookfile.write('  hosts: jobiation_inventory\\n');\n");
    tempfile.write("playbookfile.write('  gather_facts: "+options.gather_facts+"\\n');\n");
    tempfile.write("playbookfile.write('  vars:\\n');\n");
    tempfile.write("playbookfile.write('   ansible_command_timeout: "+options.ansible_command_timeout+"\\n');\n");
    tempfile.write("playbookfile.write('  tasks:\\n');\n");

    # Add write and reload if desired
    if options.reload_in >= 1:
        scfunctions.reloadIn(tempfile,options.reload_in,spaces);

    # Save facts if desired
    if options.save_facts == 1:
        scfunctions.saveFacts(tempfile,options.facts_module,spaces);

    # save output from show command if desired.
    if options.save_showcmd == 1:
        scfunctions.saveShowCmd(tempfile,options.cisco_product_line,options.showcmd,spaces);

    # Write commands
    tempfile.write("playbookfile.write('   - name: jobiation_commands\\n');\n");
    tempfile.write("playbookfile.write('     " + options.cisco_product_line + ":\\n');\n");
    tempfile.write("playbookfile.write('      commands:\\n');\n");
    tempfile.write("for cmd in commandsfile:\n");
    tempfile.write("    playbookfile.write('       - ' + cmd);\n");
    tempfile.write("playbookfile.write('\\n');\n");

    # Add when condition if desired
    if options.when_enable == 1:
        tempfile.write("playbookfile.write('     when: " + options.when_condition + "\\n');\n");

tempfile.write("with inventoryfile as invfile:\n");
tempfile.write("    invdata = csv.reader(invfile)\n");
tempfile.write("    for row in invdata:\n");

# Make an array for variables used
vars_used = [];

# Open host_conditions.py and cache in variable hostcond_content
with open('../host_conditions.py', 'r') as hostcond_file:
    hostcond_content = hostcond_file.read();

# Add required columns, columns used in host_conditions.py, and columns used in commands.txt to tempfile.py
for flCol in range(len(flList)-1):
    if flList[flCol] in req_columns:
        tempfile.write("        "+flList[flCol]+" = row["+str(flCol)+"];\n");
        if re.search("!"+flList[flCol], commands_content):
            vars_used.append(flList[flCol]);
    elif re.search("!"+flList[flCol], commands_content):
        tempfile.write("        "+flList[flCol]+" = row["+str(flCol)+"];\n");
        vars_used.append(flList[flCol]);
    elif re.search("str\\(" + flList[flCol] + "\\)", hostcond_content):
        tempfile.write("        "+flList[flCol]+" = row["+str(flCol)+"];\n"); # This line is necessary for variables used in host_conditions.py

# Add hosts_conditions.py to tempfile.py
tempfile.write(hostcond_content);

# Add commands for hosts file to tempfile.py
tempfile.write(spaces + "hostsfile.write('       ' + devicename + ':\\n');\n");
tempfile.write(spaces + "hostsfile.write('         ansible_host: ' + ip + '\\n');\n");

# Add commands for playbook file to tempfile.py
if(replacements_required >= 1):
    tempfile.write(spaces + "playbookfile.write('- name: ' + devicename + '_pb\\n');\n");
    tempfile.write(spaces + "playbookfile.write('  hosts: ' + devicename + '\\n');\n");
    tempfile.write(spaces + "playbookfile.write('  gather_facts: "+options.gather_facts+"\\n');\n");
    tempfile.write(spaces + "playbookfile.write('  vars:\\n');\n");
    tempfile.write(spaces + "playbookfile.write('   ansible_command_timeout: "+options.ansible_command_timeout+"\\n');\n");
    tempfile.write(spaces + "playbookfile.write('  tasks:\\n');\n");

    # Add write and reload if desired
    if options.reload_in >= 1:
        scfunctions.reloadIn(tempfile,options.reload_in,spaces);

    # Save facts if desired
    if options.save_facts == 1:
        scfunctions.saveFacts(tempfile,options.facts_module,spaces);

    # Save output from show command if desired.
    if options.save_showcmd == 1:
        scfunctions.saveShowCmd(tempfile,options.cisco_product_line,options.showcmd,spaces);

    # Add commands to tempfile.py
    tempfile.write(spaces + "playbookfile.write('   - name: ' + devicename + '_commands\\n');\n");
    tempfile.write(spaces + "playbookfile.write('     " + options.cisco_product_line + ":\\n');\n");
    tempfile.write(spaces + "playbookfile.write('      commands:\\n');\n");

    # Add commands for variable replacement
    tempfile.write(spaces + "commandsfile = open('commands.txt', 'r');\n");
    tempfile.write(spaces + "for cmd in commandsfile:\n");
    tempfile.write(spaces + "    repstr = cmd;\n");

    # Make replacements
    for replacement in vars_used:
        tempfile.write(spaces + "    repstr = repstr.replace('!"+replacement+"', "+replacement+");\n");
    tempfile.write(spaces + "    playbookfile.write('       - ' + repstr);\n");
    tempfile.write(spaces + "playbookfile.write('\\n');\n");

    # Add when condition if desired
    if options.when_enable == 1:
        tempfile.write(spaces + "playbookfile.write('     when: " + options.when_condition + "\\n');\n");

    # Make line between devices for easier reading.
    tempfile.write(spaces + "playbookfile.write('\\n###############################################################\\n');\n");

# Add commands to tempfile.py to close all files.
tempfile.write("\n");
tempfile.write("inventoryfile.close();\n");
tempfile.write("hostsfile.close();\n");
tempfile.write("playbookfile.close();\n");
tempfile.write("commandsfile.close();");

# Close temp file
tempfile.close();

# Execute tempfile.py
os.chmod("tmp/tempfile.py", 0o770);
exec(open("tmp/tempfile.py").read());

confirm_ready = input("Your playbook and hosts file is ready.\n\nPlease open them in " + current_dir + ".\n\nMake sure the commands are the commands you intend to perform on your Cisco devices.\n\nPress ENTER when ready.");
if(confirm_ready != ""):
    print("Aborting!");
    sys.exit();

# Create an run BASH script to run the playbook.
bashfile = open("tmp/runplaybook.sh","w");
bashfile.write('#!/bin/bash\n');
bashfile.write("/usr/bin/ansible-playbook " + current_dir + "/jobiation_task.yaml -i " + current_dir + "/hosts" + password_prompt + " > " + current_dir + "/playbook_result.txt");
bashfile.close();
os.chmod("tmp/runplaybook.sh", 0o770);
subprocess.call("tmp/runplaybook.sh");

# # Remove username and password if desired
with open(current_dir + "/hosts", "r") as hosts:
    hostslines = hosts.readlines();
with open(current_dir + "/hosts", "w") as hosts:
    for hostsline in hostslines:
        matchuser = re.search('ansible_user', hostsline)
        matchpass = re.search('ansible_password', hostsline)
        if matchuser and options.remove_username == 1:
            print("\n\nRemoving username from hosts file.\n\n");
        elif matchpass and options.remove_password == 1:
            print("\n\nRemoving password from hosts file.\n\n");
        else:
            hosts.write(hostsline);

# Remove the hosts_header file if desired
if(options.remove_hosts_header == 1):
    if os.path.exists("../hosts_header"):
        os.remove("../hosts_header");