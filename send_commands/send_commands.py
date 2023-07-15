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

# Import send_command_functions
import scfunctions;

# Make array of required columns
req_columns = [ "devicename", "ip", "active" ];

# Make sure required directories exist
functions.checkReqDir();

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

# Ask user if they want to do a write and reload
if hasattr(options, 'sc_reload_in'):
    functions.promptReload(current_dir,options.sc_reload_in,scheduled_task);

# Make a list of the first line columns of inventory.csv
flList = functions.getFirstLine(open(options.inventory_file,"r"));

# Make sure flList has required columns
functions.validateReqCol(req_columns,flList);

# Get index value of devicename
devicenameIndex = functions.getListIndex(flList,"devicename");

# Validate devicename column
functions.validateDevicename(open(options.inventory_file,"r"),validations.devicenameAllowed,current_dir,messages.badDeviceName,devicenameIndex);

# Open commands file and cache in variable commands_content
with open(options.commands_file, 'r') as commands_file:
    commands_content = commands_file.read();
commands_file.close();

# Make flag variable for replacements
replacements_required = 0;

# Increment replacements_required variable
for flCol in range(len(flList)-1):
    if re.search("!"+flList[flCol]+"!", commands_content):
        replacements_required = replacements_required+1;
    
# Validate the first line of inventory.csv
functions.validateFirstLine(flList,current_dir,messages.badFirstLine);

#Make spaces variable
if replacements_required == 0:
    spaces = "";
else:
    spaces = "        ";

# Build Hosts header if use_hosts_header == False
if(options.use_hosts_header == False):
    functions.makeHostsHeader(current_dir,options.ansible_python_interpreter,options.ansible_connection,options.ansible_network_os,options.ansible_port,username,become_necessary);

# Make temp python file
tempfile = open("tmp/tempfile.py","w");

# Add shebang and imports to tempfile.py
tempfile.write("#!/usr/bin/env python3\n");
tempfile.write("import csv\n");

# Open files in tempfile.py
tempfile.write("hostsfile = open('" + current_dir + "/hosts.yaml', 'a+');\n");
tempfile.write("inventoryfile = open('"+options.inventory_file+"', 'r');\n");
tempfile.write("commandsfile = open('"+options.commands_file+"', 'r');\n");
tempfile.write("playbookfile = open('" + current_dir + "/jobiation_task.yaml', 'w');\n");
tempfile.write("playbookfile.write('---\\n');\n");

# Write to playbook file in tempfile.py if replacements required
if(replacements_required == 0):
    tempfile.write("playbookfile.write('- name: jobiation_pb\\n');\n");
    tempfile.write("playbookfile.write('  hosts: jobiation_inventory\\n');\n");
    tempfile.write("playbookfile.write('  gather_facts: "+options.gather_facts+"\\n');\n");
    tempfile.write("playbookfile.write('  vars:\\n');\n");
    tempfile.write("playbookfile.write('   ansible_command_timeout: "+str(options.ansible_command_timeout)+"\\n');\n");
    tempfile.write("playbookfile.write('  tasks:\\n');\n");

    # Add write and reload if desired
    if hasattr(options, 'sc_reload_in'):
        functions.reloadIn(tempfile,options.sc_reload_in,spaces);
    
    # Add revert commands if desired
    if hasattr(options,'revert_timer'):
        functions.setRevertTimer(tempfile,spaces,options.cisco_command_type,options.revert_timer,options.archive_path);

    # Save facts if desired
    if hasattr(options, 'sc_facts_output'):
        scfunctions.saveFacts(tempfile,options.sc_facts_output,spaces);

    # save output from show command if desired.
    if hasattr(options, 'showcmd'):
        scfunctions.saveShowCmd(tempfile,options.cisco_command_type,options.showcmd,spaces);

    # Write commands
    tempfile.write("playbookfile.write('   - name: jobiation_commands\\n');\n");
    tempfile.write("playbookfile.write('     " + options.cisco_command_type + ":\\n');\n");
    tempfile.write("playbookfile.write('      commands:\\n');\n");
    tempfile.write("for cmd in commandsfile:\n");
    tempfile.write("    playbookfile.write('       - ' + cmd);\n");
    tempfile.write("playbookfile.write('\\n');\n");

    # Add when condition if desired
    if hasattr(options, 'when_condition'):
        tempfile.write("playbookfile.write('     when: " + options.when_condition + "\\n');\n");

    # Confirm config if desired
    if hasattr(options,'config_confirm'):
        if options.config_confirm:
            functions.confirmConfig(tempfile,spaces,options.cisco_command_type);

# Interate through inventory file
tempfile.write("with inventoryfile as invfile:\n");
tempfile.write("    invdata = csv.reader(invfile)\n");
tempfile.write("    for row in invdata:\n");

# Make an array for variables used
vars_used = [];

# Open host_conditions.py and cache in variable hostcond_content
with open(options.host_conditions_file, 'r') as hostcond_file:
    hostcond_content = hostcond_file.read();
hostcond_file.close();

# Add required columns, columns used in host_conditions.py, and columns used in the commands_file to tempfile.py
for flCol in range(len(flList)-1):
    if flList[flCol] in req_columns:
        tempfile.write("        "+flList[flCol]+" = row["+str(flCol)+"];\n");
        if re.search("!"+flList[flCol]+"!", commands_content):
            vars_used.append(flList[flCol]);
    elif re.search("!"+flList[flCol]+"!", commands_content):
        tempfile.write("        "+flList[flCol]+" = row["+str(flCol)+"];\n");
        vars_used.append(flList[flCol]);
    elif re.search("str\\(" + flList[flCol] + "\\)", hostcond_content):
        tempfile.write("        "+flList[flCol]+" = row["+str(flCol)+"];\n"); # This line is necessary for variables used in host_conditions.py

# Add hosts_conditions.py to tempfile.py
tempfile.write(hostcond_content);

# Add commands for hosts file to tempfile.py
tempfile.write("        hostsfile.write('       ' + devicename + ':\\n');\n");
tempfile.write("        hostsfile.write('         ansible_host: ' + ip + '\\n');\n");

# Add commands for playbook file to tempfile.py
if(replacements_required >= 1):
    tempfile.write(spaces + "playbookfile.write('- name: ' + devicename + '_pb\\n');\n");
    tempfile.write(spaces + "playbookfile.write('  hosts: ' + devicename + '\\n');\n");
    tempfile.write(spaces + "playbookfile.write('  gather_facts: "+options.gather_facts+"\\n');\n");
    tempfile.write(spaces + "playbookfile.write('  vars:\\n');\n");
    tempfile.write(spaces + "playbookfile.write('   ansible_command_timeout: "+str(options.ansible_command_timeout)+"\\n');\n");
    tempfile.write(spaces + "playbookfile.write('  tasks:\\n');\n");

    # Add write and reload if desired
    if hasattr(options, 'sc_reload_in'):
        functions.reloadIn(tempfile,options.sc_reload_in,spaces);

    # Add revert commands if desired
    if hasattr(options,'revert_timer'):
        functions.setRevertTimer(tempfile,spaces,options.cisco_command_type,options.revert_timer,options.archive_path);

    # Save facts if desired
    if hasattr(options, 'sc_facts_output'):
        scfunctions.saveFacts(tempfile,options.sc_facts_output,spaces);

    # Save output from show command if desired.
    if hasattr(options, 'showcmd'):
        scfunctions.saveShowCmd(tempfile,options.cisco_command_type,options.showcmd,spaces);

    # Add commands to tempfile.py
    tempfile.write(spaces + "playbookfile.write('   - name: ' + devicename + '_commands\\n');\n");
    tempfile.write(spaces + "playbookfile.write('     " + options.cisco_command_type + ":\\n');\n");
    tempfile.write(spaces + "playbookfile.write('      commands:\\n');\n");

    # Add commands for variable replacement
    tempfile.write(spaces + "commandsfile = open('"+options.commands_file+"', 'r');\n");
    tempfile.write(spaces + "for cmd in commandsfile:\n");
    tempfile.write(spaces + "    repstr = cmd;\n");

    # Make replacements
    for replacement in vars_used:
        tempfile.write(spaces + "    repstr = repstr.replace('!"+replacement+"!', "+replacement+");\n");
    tempfile.write(spaces + "    playbookfile.write('       - ' + repstr);\n");
    tempfile.write(spaces + "playbookfile.write('\\n');\n");

    # Add when condition if desired
    if hasattr(options, 'when_condition'):
        tempfile.write(spaces + "playbookfile.write('     when: " + options.when_condition + "\\n');\n");

    # Add revert commands if desired
    if hasattr(options,'config_confirm'):
        if options.config_confirm:
            functions.confirmConfig(tempfile,spaces,options.cisco_command_type);

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

# Notify if task failed.
if hasattr(options,"notify_script") and hasattr(options,"notify_recipients") and hasattr(options,"notify_subject"):
    functions.notifyFailure(options.notify_script,options.notify_recipients,options.notify_subject,current_dir,"get_output");