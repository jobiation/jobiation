#!/usr/bin/env python3

#    Copyright 2023 Anthony Tranquillo

#    This file is part of Jobiation.

#    Jobiation is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

#    Jobiation is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License along with Jobiation.  If not, see <http://www.gnu.org/licenses/>.

# Imports
import sys;
import shutil;
import os;
from datetime import datetime;
import re;

# Import options and functions modules
sys.path.insert(1, '../');
import functions;
import validations;
import messages;
import options;

# Check argument and set commands_file variable
if len(sys.argv) > 1:
    playbook = open(sys.argv[1],"r");
else:
    print("This script requires an argument specifying a playbook file.");
    sys.exit();

# Validate the task name
functions.validateArg(validations.argNameAllowed,sys.argv[1],messages.badArgNameMsg);

# Make sure required directories exist
functions.checkReqDir();

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
firstline = functions.getFirstLine(open(options.inventory_file,"r"));
for col in firstline:
    if col == "ip":
        ipIndex = firstline.index(col);

# Get index of devicename column
devicenameIndex = "";
firstline = functions.getFirstLine(open(options.inventory_file,"r"));
for col in firstline:
    if col == "devicename":
        devicenameIndex = firstline.index(col);

# Open inventory file again because the getFirstLine() def closes it.
inventoryfile = open(options.inventory_file,"r");

# Get IP from inventory file
ip = 0;
with inventoryfile as inventoryfile_as:
    for invline in inventoryfile_as:
        invline_split = invline.split(",");
        if invline_split[devicenameIndex] == host:
            ip = invline_split[ipIndex];

# Close inventoryfile
inventoryfile.close();

# Get current date and time
now = datetime.now() # current date and time
date_time = now.strftime("%Y%m%d_%H%M");

# # Make a directory for the job
current_dir = functions.makeCurrentDir(date_time,options.prepend_job_name);

# Copy hosts_header or check if username is needed in the options file
password_prompt = "";
username = "";
become_necessary = "no";

if options.use_hosts_header:
    if not os.path.exists(options.hosts_header):
        print(messages.noHostsHeader);
        shutil.rmtree(current_dir);
        sys.exit();
    shutil.copyfile(options.hosts_header, current_dir + "/hosts.yaml");
    username = "NA";
else:
    if(options.ansible_user == ""):
        username = input(messages.noUsername);
    else:
        username = options.ansible_user;
    
    become_password = input("Do your devices need an enable password? [y/n] ");

    if become_password.lower() == "y":
        password_prompt = " -k -K";
        become_necessary = "yes";   
    else:
        password_prompt = " -k";

# Build hosts file
if(options.use_hosts_header == False):
    functions.makeHostsHeader(current_dir,options.ansible_python_interpreter,options.ansible_connection,options.ansible_network_os,options.ansible_port,username,become_necessary);
else:
    hostsfile = open(current_dir+"/hosts.yaml","a+");

# Add host to host's header
hostsfile.write("       " + host + ":\n");
hostsfile.write("         ansible_host: " + str(ip) + "\n");

# Close hostsfile
hostsfile.close();

# Copy playbook to current_dir
shutil.copyfile(sys.argv[1], current_dir + "/jobiation_task.yaml");

# Convert line endings if desired
if hasattr(options,"convert_pb_line_end"):
    if options.convert_pb_line_end:
        functions.convertLineEnd(current_dir,"jabiation_task.yaml");
if hasattr(options,"convert_host_line_end"):
    if options.convert_host_line_end:
        functions.convertLineEnd(current_dir,"hosts.yaml");

# Confirm user is ready
functions.confirmReady(current_dir,"NA");

# Create an run BASH script to run the playbook.
functions.runPlaybook(current_dir,current_dir+"/jobiation_task.yaml",password_prompt,"\nRunning playbook.\n","\nPlaybook finished running.\n","playbook_results.txt",options.ansible_exe);

# # Remove username and password if desired
if hasattr(options,"use_hosts_header"):
    if options.use_hosts_header:
        if hasattr(options,"remove_become"):
            if options.remove_become:
                functions.removeBecome(current_dir);
        if hasattr(options,"remove_username"):
            if options.remove_username:
                functions.removeUser(current_dir);
        if hasattr(options,"remove_password"):
            if options.remove_password:
                functions.removePass(current_dir);

# Remove the hosts_header file if desired
if hasattr(options, "remove_hosts_header"):
    if options.remove_hosts_header:
        functions.removeHostsHeader(options.hosts_header);