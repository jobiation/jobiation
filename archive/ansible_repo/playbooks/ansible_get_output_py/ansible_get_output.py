#!/usr/bin/env python3

# User options
rootdir = "/var/ansiblerepo/playbooks/ansible_get_output_py";

# Imports
import csv
import sys # For exiting the script early with sys.exit();
import shutil # For copyfile
import os # For mkdir
from datetime import datetime

def catFiles():
    filenames = ["scriptcache/header.py", "scriptcache/columns.py", "host_conditions.py", "scriptcache/footer.py"]
    with open("scriptcache/completefile.py", "w+") as new_file:
        for name in filenames:
            with open(name) as f:
                for line in f:
                    new_file.write(line)

# Get current date and time
now = datetime.now() # current date and time
date_time = now.strftime("%Y%m%d_%H%M");

# # Make the working directory
os.mkdir('jobs/' + date_time);
current_dir = rootdir + "/jobs/" + date_time;

# open ansibledevices.csv
devicesfile = open("ansibledevices.csv","r");
columnsfile = open("scriptcache/columns.py","w");

# Make the array of the first line
# with open("ansibledevices.csv", "r") as file:
with devicesfile as devicesrow:
    firstline = devicesrow.readline()
flList = firstline.split(",");

# Populate columns.py
for flCol in range(len(flList)-1):
    columnsfile.write("        " + flList[flCol] + " = row[" + str(flCol) + "];" + "\n");

# Must be closed here or it does not concatinate nicely with the header and footer
columnsfile.close();

catFiles();
os.chmod("scriptcache/completefile.py", 0o770);

# Copy the hosts_header and playbook_header.yaml
shutil.copyfile("scriptcache/hosts_header", "hosts")

# Execute the completefile.py
exec(open("scriptcache/completefile.py").read());

# hosts and ansible_task.yaml to the current directory
shutil.copyfile("scriptcache/ansible_task.yaml", current_dir + "/ansible_task.yaml");
shutil.copyfile("hosts", "/etc/ansible/hosts");
shutil.move("hosts", current_dir + "/hosts");

import subprocess

bashfile = open("scriptcache/runplaybook.sh","w");
bashfile.write('#!/bin/bash\n');
bashfile.write("/usr/bin/ansible-playbook --vault-id ansiblevaultuser@/var/cons/.ansiblecreds " + current_dir + "/ansible_task.yaml > " + current_dir + "/playbook_result.txt");
bashfile.close();
os.chmod("scriptcache/runplaybook.sh", 0o770);

subprocess.call("scriptcache/runplaybook.sh")

# Close the text file
devicesfile.close();

# rm /etc/ansible/hosts



################### References 

# # Import vars.py
# import vars
# print(vars.showcmd);

# sys.exit();
