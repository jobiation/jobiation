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
import pathlib;

# Set a value os schedule_task if it is a scheduled task
scheduled_task = "NA";
if len(sys.argv) > 1:
    scheduled_task = sys.argv[1];
    sys.path.insert(1, './scheduled_tasks/'+scheduled_task);
    import options;

# Import options and functions modules
sys.path.insert(1, '../');
if scheduled_task == "NA":
    import options;
import functions;
import validations;
import messages;

# Validate the task name
functions.validateArg(validations.argNameAllowed,scheduled_task,messages.badArgNameMsg);

# Import gofunctions modules
import gofunctions;

# Make list of required columns
req_columns = [ "devicename", "ip", "active" ];

# Make sure required directories exist
functions.checkReqDir();

# Get current date and time
now = datetime.now() # current date and time
date_time = now.strftime("%Y%m%d_%H%M");

# # Make a directory for the job
current_dir = functions.makeCurrentDir(date_time,options.prepend_job_name);

# Make a list of the first line columns of inventory.csv
flList = functions.getFirstLine(open(options.inventory_file,"r"));

# Make sure flList has required columns
functions.validateReqCol(req_columns,flList);

# Get index value of devicename
devicenameIndex = functions.getListIndex(flList,"devicename");

# Validate devicename column
functions.validateDevicename(open(options.inventory_file,"r"),validations.devicenameAllowed,current_dir,messages.badDeviceName,devicenameIndex);

# Declare variables from options files
go_facts_output = 0;
showcmd_exports = 0;

# Set go_facts_output variable
if hasattr(options, 'go_facts_output'):
    go_facts_output = 1;

# Set showcnd_exports variable
if len(options.showcmd_exports) >= 1:
    showcmd_exports = 1;

# Check if there is anything to do
if go_facts_output == 0 and showcmd_exports == 0:
    print("\ngo_facts_output is not set and showcmd_exports is null so there is nothing to do. Please check options.py.\n");
    shutil.rmtree(current_dir);
    sys.exit();

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

# Validate the first line of inventory.csv
functions.validateFirstLine(flList,current_dir,messages.badFirstLine);

# Build Hosts header if use_hosts_header == False
if(options.use_hosts_header == False):
    functions.makeHostsHeader(current_dir,options.ansible_python_interpreter,options.ansible_connection,options.ansible_network_os,options.ansible_port,username,become_necessary);

# Make temp python file
tempfile = open("tmp/tempfile.py","w");

# Add shebang and imports to tempfile.py
tempfile.write("#!/usr/bin/env python3\n");
tempfile.write("import csv\n");
tempfile.write("import sys\n");
tempfile.write("import shutil\n");
tempfile.write("import os\n");

# Open files in tempfile.py
tempfile.write("hostsfile = open('" + current_dir + "/hosts.yaml', 'a+');\n");
tempfile.write("inventoryfile = open('"+options.inventory_file+"', 'r');\n");
tempfile.write("playbookfile = open('" + current_dir + "/jobiation_task.yaml', 'w');\n");
tempfile.write("playbookfile.write('---\\n');\n");

# Write to playbook file in tempfile.py if replacements required
tempfile.write("playbookfile.write('- name: jobiation_pb\\n');\n");
tempfile.write("playbookfile.write('  hosts: jobiation_inventory\\n');\n");
tempfile.write("playbookfile.write('  gather_facts: "+options.gather_facts+"\\n');\n");
tempfile.write("playbookfile.write('  vars:\\n');\n");
tempfile.write("playbookfile.write('   ansible_command_timeout: "+str(options.ansible_command_timeout)+"\\n');\n");
tempfile.write("playbookfile.write('  tasks:\\n');\n");

# Save facts if desired
if hasattr(options, 'go_facts_output'):
    os.mkdir(current_dir+"/facts");
    gofunctions.saveFacts(tempfile,options.go_facts_output,current_dir);

# save output from show command if desired and validate user defined dictionary
if len(options.showcmd_exports) >= 1:
    for subdir in options.showcmd_exports:
        if re.search(validations.dictAllowedChars, subdir):
            os.mkdir(current_dir+"/"+subdir);
            gofunctions.saveShowCmd(tempfile,options.cisco_command_type,options.showcmd_exports[subdir],subdir,current_dir);
        else:
            functions.abortPlaybook(current_dir,"\n!"+subdir+messages.badDictKey,True);

# Interate through inventory file
tempfile.write("with inventoryfile as invfile:\n");
tempfile.write("    invdata = csv.reader(invfile)\n");
tempfile.write("    for row in invdata:\n");

# Open host_conditions.py and cache in variable hostcond_content
with open(options.host_conditions_file, 'r') as hostcond_file:
    hostcond_content = hostcond_file.read();
hostcond_file.close();

# Add required columns and columns used in host_conditions.py
for flCol in range(len(flList)-1):
    if flList[flCol] in req_columns:
        tempfile.write("        "+flList[flCol]+" = row["+str(flCol)+"];\n");
    elif re.search("str\\(" + flList[flCol] + "\\)", hostcond_content):
        tempfile.write("        "+flList[flCol]+" = row["+str(flCol)+"];\n"); # This line is necessary for variables used in host_conditions.py

# Add hosts_conditions.py to tempfile.py
tempfile.write(hostcond_content);

# Add commands for hosts file to tempfile.py
tempfile.write("        hostsfile.write('       ' + devicename + ':\\n');\n");
tempfile.write("        hostsfile.write('         ansible_host: ' + ip + '\\n');\n");

# Add commands to tempfile.py to close all files.
tempfile.write("\n");
tempfile.write("inventoryfile.close();\n");
tempfile.write("hostsfile.close();\n");
tempfile.write("playbookfile.close();\n");

# Close temp file
tempfile.close();

# Execute tempfile.py
os.chmod("tmp/tempfile.py", 0o770);
exec(open("tmp/tempfile.py").read());

# Convert line endings if desired
if hasattr(options,"convert_pb_line_end"):
    if options.convert_pb_line_end:
        functions.convertLineEnd(current_dir,"jabiation_task.yaml");
if hasattr(options,"convert_host_line_end"):
    if options.convert_host_line_end:
        functions.convertLineEnd(current_dir,"hosts.yaml");

# Confirm user is ready
functions.confirmReady(current_dir,scheduled_task);

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

# Remove sensitive data
dirs = options.commands_to_remove;

for dir in dirs:
    if re.search(validations.dictAllowedChars, dir):
        cmds_to_remove = str(dirs[dir]);
        subdirlist = pathlib.Path(current_dir+"/"+dir).iterdir();
        for cmdfile in subdirlist:
            gofunctions.cleanFile(cmdfile,cmds_to_remove);
    else:
        functions.abortPlaybook(current_dir,"\n!"+dir+messages.badDictKey,True);

# Notify if task failed.
if hasattr(options,"notify_script") and hasattr(options,"notify_recipients") and hasattr(options,"notify_subject"):
    functions.notifyFailure(options.notify_script,options.notify_recipients,options.notify_subject,current_dir,"get_output");
