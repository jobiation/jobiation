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
# if options.use_hosts_header == 0:
#     print("Not using hosts header");

# Import functions
sys.path.insert(1, '../common/');
import functions

# Get current date and time
now = datetime.now() # current date and time
date_time = now.strftime("%Y%m%d_%H%M");

# # Make a directory for the job
os.mkdir('jobs/' + date_time);
current_dir = "jobs/" + date_time;

# Check if username is needed
if(options.use_hosts_header == 1):
    print("Using hosts header");
    shutil.copyfile("../common/hosts_header", "jobs/hosts");
    username = "NA";
elif(options.ansible_user == ""):
    username = input("You do not have a username set. What username do you want to use? ");
else:
    username = options.ansible_user;

# Build Hosts header if use_hosts_headeer == 0
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

# Make variable for replacements
replacements_required = 0;

# Increment replacements_required variable
for flCol in range(len(flList)-1):
    if re.search("!"+flList[flCol], commands_content):
        replacements_required = replacements_required+1;

# Set spacing
# spacing = "    ";
# if(replacements_required >= 1):
#     spacing = "    ";
#     print("spacing if executed");

# Make temp python file
tempfile = open("tempfile.py","w");

# Add first part of script to tempfile.py
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

if(replacements_required == 0):
    tempfile.write("playbookfile.write('- name: jobiation_pb\\n');\n");
    tempfile.write("playbookfile.write('  hosts: jobiation_inventory\\n');\n");
    tempfile.write("playbookfile.write('  gather_facts: "+options.gather_facts+"\\n');\n");
    tempfile.write("playbookfile.write('  vars:\\n');\n");
    tempfile.write("playbookfile.write('   ansible_command_timeout: "+options.ansible_command_timeout+"\\n');\n");
    tempfile.write("playbookfile.write('  tasks:\\n');\n");
    tempfile.write("playbookfile.write('   - name: jobiation_commands\\n');\n");
    tempfile.write("playbookfile.write('     " + options.cisco_product_line + ":\\n');\n");
    tempfile.write("playbookfile.write('      commands:\\n');\n");
    tempfile.write("for cmd in commandsfile:\n");
    tempfile.write("    playbookfile.write('       - ' + cmd);\n");

tempfile.write("with inventoryfile as csvfile:\n");
tempfile.write("    datareader = csv.reader(csvfile)\n");
tempfile.write("    for row in datareader:\n");

# Make an array for variables used
vars_used = [];

# Open host_conditions.py and cache in variable hostcond_content
with open('../host_conditions.py', 'r') as hostcond_file:
    hostcond_content = hostcond_file.read();

# Add required and used columns
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

# Add host conditions
filenames = ["../host_conditions.py"]
for name in filenames:
    with open(name) as f:
        for line in f:
            tempfile.write(line)

# Add commands for hosts file and playbook file
tempfile.write("        hostsfile.write('       ' + devicename + ':\\n');\n");
tempfile.write("        hostsfile.write('         ansible_host: ' + ip + '\\n');\n");

if(replacements_required >= 1):
    tempfile.write("        playbookfile.write('- name: ' + devicename + '_pb\\n');\n");
    tempfile.write("        playbookfile.write('  hosts: ' + devicename + '\\n');\n");
    tempfile.write("        playbookfile.write('  gather_facts: "+options.gather_facts+"\\n');\n");
    tempfile.write("        playbookfile.write('  vars:\\n');\n");
    tempfile.write("        playbookfile.write('   ansible_command_timeout: "+options.ansible_command_timeout+"\\n');\n");
    tempfile.write("        playbookfile.write('  tasks:\\n');\n");
    tempfile.write("        playbookfile.write('   - name: ' + devicename + '_commands\\n');\n");
    tempfile.write("        playbookfile.write('     " + options.cisco_product_line + ":\\n');\n");
    tempfile.write("        playbookfile.write('      commands:\\n');\n");

    # Add commands for variable replacement
    tempfile.write("        commandsfile = open('commands.txt', 'r');\n");
    tempfile.write("        for cmd in commandsfile:\n");
    tempfile.write("            repstr = cmd;\n");

    for replacement in vars_used:
        tempfile.write("            repstr = repstr.replace('!"+replacement+"', "+replacement+");\n");

    tempfile.write("            playbookfile.write('       - ' + repstr);\n");
    tempfile.write("        playbookfile.write('\\n###############################################################\\n');\n");

# Add commands to close all files tempfile.py will open when it is executed

tempfile.write("\n");
tempfile.write("inventoryfile.close();\n");
tempfile.write("hostsfile.close();\n");
tempfile.write("playbookfile.close();\n");
tempfile.write("commandsfile.close();");

os.chmod("tempfile.py", 0o770);

tempfile.close();

# Execute the the compiled file completefile.py
exec(open("tempfile.py").read());

bashfile = open("tmp/runplaybook.sh","w");
bashfile.write('#!/bin/bash\n');

if(options.use_hosts_header == 1):
    bashfile.write("/usr/bin/ansible-playbook --vault-id ansiblevaultuser@/var/cons/.ansiblecreds " + current_dir + "/ansible_task.yaml > " + current_dir + "/playbook_result.txt");
else:
    bashfile.write("/usr/bin/ansible-playbook " + current_dir + "/jobiation_task.yaml -i " + current_dir + "/hosts -k > " + current_dir + "/playbook_result.txt");
bashfile.close();
os.chmod("tmp/runplaybook.sh", 0o770);

subprocess.call("tmp/runplaybook.sh")
