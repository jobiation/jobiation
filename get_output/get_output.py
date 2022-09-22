#!/usr/bin/env python3

# Imports
import csv
import sys # For exiting the script early with sys.exit();
import shutil # For copyfile
import os # For mkdir
from datetime import datetime
import subprocess # For running a bash script

# Import options
sys.path.insert(1, '../');
import options
# if options.use_hosts_header == 0:
#     print("Not using hosts header");

# Import functions
sys.path.insert(1, '../common/');
import functions

# Check if username is needed

if(options.use_hosts_header == 1):
    print("Using hosts header");
    username = "NA";
elif(options.use_hosts_header == 0 and options.ansible_user == ""):
    username = input("You do not have a username set. What username do you want to use? ");
else:
    username = options.ansible_user;

print(username);

sys.exit();

# Get current date and time
now = datetime.now() # current date and time
date_time = now.strftime("%Y%m%d_%H%M");

# # Make the working directory
os.mkdir('jobs/' + date_time);
current_dir = "jobs/" + date_time;

# Build Hosts header
if(options.use_hosts_header == 1):
    shutil.copyfile("../common/hosts_header", "tmp/hosts");
else:
    functions.buildHosts(options.ansible_python_interpreter, options.ansible_connection, options.ansible_network_os, options.ansible_port, username);

# open ansibledevices.csv
inventoryfile = open("../inventory.csv","r");
columnsfile = open("scriptfiles/columns.py","w");

# Make the array of the first line
with inventoryfile as invrow:
    firstline = invrow.readline()
flList = firstline.split(",");

# Populate columns.py
for flCol in range(len(flList)-1):
    columnsfile.write("        " + flList[flCol] + " = row[" + str(flCol) + "];" + "\n");

# Close columnsfile
# Must be closed here or it does not concatinate nicely with the header and footer
columnsfile.close();

# Concatinate files in and set permissions
functions.catFiles();
os.chmod("scriptfiles/compiled.py", 0o770);

# Execute the the compiled file completefile.py
exec(open("scriptfiles/compiled.py").read());

# hosts and ansible_task.yaml to the current directory
shutil.copyfile("scriptfiles/ansible_task.yaml", current_dir + "/ansible_task.yaml");
shutil.copyfile("tmp/hosts", "/etc/ansible/hosts");
shutil.move("tmp/hosts", current_dir + "/hosts");

bashfile = open("tmp/runplaybook.sh","w");
bashfile.write('#!/bin/bash\n');

if(options.use_hosts_header == 1):
    bashfile.write("/usr/bin/ansible-playbook --vault-id ansiblevaultuser@/var/cons/.ansiblecreds " + current_dir + "/ansible_task.yaml > " + current_dir + "/playbook_result.txt");
else:
    bashfile.write("/usr/bin/ansible-playbook --vault-id ansiblevaultuser@/var/cons/.ansiblecreds " + current_dir + "/ansible_task.yaml -k > " + current_dir + "/playbook_result.txt");
bashfile.close();
os.chmod("tmp/runplaybook.sh", 0o770);

subprocess.call("tmp/runplaybook.sh")

# Cleanup file
# Remove tmp and tmp/output

# Close the text file
inventoryfile.close();

# rm /etc/ansible/hosts



################### References 

# # Import vars.py
# import vars
# print(vars.showcmd);

# sys.exit();
