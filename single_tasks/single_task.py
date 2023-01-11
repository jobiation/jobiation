#!/usr/bin/env python3

# Imports
import sys;
import shutil;
import os;
from datetime import datetime;
import subprocess;
import re;

# Get playbook file from sys.argv
playbook = open(sys.argv[1],"r");

# Import options and functions files
sys.path.insert(1, '../');
import options;
import functions;

# Get host from playbook file
host = "";
matchHost =re.compile("^  hosts: ");
with playbook as playbook_as:
    for pbline in playbook_as:
        if re.search(matchHost, pbline):
            host = pbline.replace("  hosts: ","");
            host = host.replace("\n","");

# Get index of IP column
ipIndex = 0;
firstline = functions.getFirstLine(open("../inventory.csv","r"));
for col in firstline:
    if col == "ip":
        ipIndex = firstline.index(col);

# Open inventory file again because the getFirstLine() def closes it.
inventoryfile = open("../inventory.csv","r");

# Get IP from inventory file
ip = 0;
with inventoryfile as inventoryfile_as:
    for invline in inventoryfile_as:
        invline_split = invline.split(",");
        if invline_split[0] == host:
            ip = invline_split[2];

# Close inventoryfile
inventoryfile.close();

# Get current date and time
now = datetime.now() # current date and time
date_time = now.strftime("%Y%m%d_%H%M");

# # Make a directory for the job
if os.path.isdir('jobs/' + date_time):
    print("\nYou cannot run more than one job within the same minute. Please wait until the end of this minute and try again.\n");
    sys.exit();
else:
    os.mkdir('jobs/' + date_time);
    current_dir = "jobs/" + date_time;

# Copy hosts_header or check if username is needed in the options file
password_prompt = " -k";

if(options.use_hosts_header == True):
    if not os.path.exists("../hosts_header"):
        input("\nYou need to put a hosts_header file in the jobiation root when you set the use_hosts_header to True in options.py.\n");
        shutil.rmtree(current_dir);
        sys.exit();
    shutil.copyfile("../hosts_header", current_dir + "/hosts");
    username = "NA";
    password_prompt = "";
elif(options.ansible_user == ""):
    username = input("\nYou do not have a username set. What username do you want to use? ");
else:
    username = options.ansible_user;

# Build hosts file
if(options.use_hosts_header == False):
    hostsfile = open(current_dir+"/hosts","w");
    hostsfile.write("---\n");
    hostsfile.write("all:\n");   
    hostsfile.write(" vars:\n");
    hostsfile.write("  ansible_python_interpreter: " + options.ansible_python_interpreter + "\n");
    hostsfile.write("  ansible_connection: " + options.ansible_connection + "\n");
    hostsfile.write("  ansible_network_os: " + options.ansible_network_os + "\n");
    hostsfile.write("  ansible_port: " + str(options.ansible_port) + "\n");
    hostsfile.write("  ansible_user: " + username + "\n");
    hostsfile.write(" children:\n");
    hostsfile.write("   jobiation_inventory:\n");
    hostsfile.write("     hosts:\n");
else:
    hostsfile = open(current_dir+"/hosts","a+");

# Add host to host's header
hostsfile.write("       " + host + ":\n");
hostsfile.write("         ansible_host: " + ip + "\n");

# Close hostsfile
hostsfile.close();

# Copy playbook to current_dir
shutil.copyfile(sys.argv[1], current_dir + "/jobiation_task.yaml");

# Confirm user is ready
confirm_ready = input("\n\n-- Your playbook and hosts file is ready.\n\n-- Please open them in " + current_dir + ".\n\n-- Make sure the commands are the commands you intend to perform on your Cisco devices.\n\n-- Press ENTER when ready or type quit.\n\n");
if(confirm_ready != ""):
    print("\nAborting!\n");
    shutil.rmtree(current_dir);
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
hosts.close();
with open(current_dir + "/hosts", "w") as hosts:
    for hostsline in hostslines:
        matchuser = re.search('ansible_user', hostsline)
        matchpass = re.search('ansible_password', hostsline)
        if matchuser and options.remove_username == True:
            print("\n\nRemoving username from hosts file.\n\n");
        elif matchpass and options.remove_password == True:
            print("\n\nRemoving password from hosts file.\n\n");
        else:
            hosts.write(hostsline);
hosts.close();

# Remove the hosts_header file if desired
if(options.remove_hosts_header == True):
    if os.path.exists("../hosts_header"):
        os.remove("../hosts_header");
