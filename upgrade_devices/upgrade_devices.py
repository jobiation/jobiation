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
import csv;
import math;

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

# Make array of required columns
req_columns = [ "devicename", "ip", "active" ];

# Make sure required directories exist
functions.checkReqDir();

# Make sure the user has at least one of the required options uncommented.
if not hasattr(options,"ud_file_copy"):
    if not hasattr(options,"ud_boot_sys_cmd"):
        if not hasattr(options,"ud_reload_in"):
            print("\nYou have ud_file_copy, ud_boot_sys_cmd, and ud_reload_in\nThere is nothing to do\n");
            sys.exit();

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
if hasattr(options, 'reload_in'):
    functions.promptReload(current_dir,options.reload_in);

# Make a list of the first line columns of inventory.csv
flList = functions.getFirstLine(open(options.inventory_file,"r"));

# Make sure flList has required columns
functions.validateReqCol(req_columns,flList);

# Get index value of devicename
devicenameIndex = functions.getListIndex(flList,"devicename");

# Validate devicename column
functions.validateDevicename(open(options.inventory_file,"r"),validations.devicenameAllowed,current_dir,messages.badDeviceName,devicenameIndex);

# Validate the first line of inventory.csv
functions.validateFirstLine(flList,current_dir,messages.badFirstLine);

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
tempfile.write("playbookfile = open('" + current_dir + "/gather_facts.yaml', 'w');\n");
tempfile.write("playbookfile.write('---\\n');\n");

# Interate through inventory file
tempfile.write("with inventoryfile as invfile:\n");
tempfile.write("    invdata = csv.reader(invfile)\n");
tempfile.write("    for row in invdata:\n");

# Open host_conditions.py and cache in variable hostcond_content
with open(options.host_conditions_file, 'r') as hostcond_file:
    hostcond_content = hostcond_file.read();
hostcond_file.close();

# Add required columns, columns used in host_conditions.py, and columns used in the commands_file to tempfile.py
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

# Add commands for playbook file to tempfile.py
tempfile.write(spaces + "playbookfile.write('- name: ' + devicename + '_pb\\n');\n");
tempfile.write(spaces + "playbookfile.write('  hosts: ' + devicename + '\\n');\n");
tempfile.write(spaces + "playbookfile.write('  gather_facts: "+options.gather_facts+"\\n');\n");
tempfile.write(spaces + "playbookfile.write('  vars:\\n');\n");
tempfile.write(spaces + "playbookfile.write('   ansible_command_timeout: "+str(options.ansible_command_timeout)+"\\n');\n");
tempfile.write(spaces + "playbookfile.write('  tasks:\\n');\n");

# Get current boot image
bootsysfile = open("tmp/bootsys_cmds.txt","w");
bootsysfile.close();
tempfile.write(spaces+"playbookfile.write('   - name: gather_facts_image\\n');\n");
tempfile.write(spaces+"playbookfile.write('     " + options.ud_facts_output + ":\\n');\n");
tempfile.write(spaces+"playbookfile.write('     register: image_output\\n');\n");
tempfile.write(spaces+"playbookfile.write('   - name: copy_image_to_file\\n');\n");
tempfile.write(spaces+"playbookfile.write('     lineinfile: path=\"tmp/bootsys_cmds.txt\" line=\"{{ inventory_hostname }},{{ image_output" + options.old_image_file + " }}\" insertafter=EOF state=present\\n');\n");

# Get current boot image
newfile = open("tmp/freespace.txt","w");
newfile.close();
tempfile.write(spaces+"playbookfile.write('   - name: gather_facts_fspace\\n');\n");
tempfile.write(spaces+"playbookfile.write('     " + options.ud_facts_output + ":\\n');\n");
tempfile.write(spaces+"playbookfile.write('     register: fspace_output\\n');\n");
tempfile.write(spaces+"playbookfile.write('   - name: copy_fspace_to_file\\n');\n");
tempfile.write(spaces+"playbookfile.write('     lineinfile: path=\"tmp/freespace.txt\" line=\"{{ inventory_hostname }},{{ fspace_output" + options.free_space + " }}\" insertafter=EOF state=present\\n');\n");

# Make line between devices for easier reading.
tempfile.write(spaces + "playbookfile.write('\\n###############################################################\\n');\n");

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
        functions.convertLineEnd(current_dir,"gather_facts.yaml");
if hasattr(options,"convert_host_line_end"):
    if options.convert_host_line_end:
        functions.convertLineEnd(current_dir,"hosts.yaml");

# Create an run BASH script to run the playbook.
functions.runPlaybook(current_dir,current_dir+"/gather_facts.yaml",password_prompt,"\nGetting boot system commands and free space.\n\nThis could take a long time if there are several devices to upgrade\n","\n","gather_facts_results.txt",options.ansible_exe);

######################################################################################################

# Start playbook file
playbookfile = open(current_dir + '/jobiation_task.yaml', 'w');
playbookfile.write('---\n');

# Start upgrade resuls file.
upgrade_skips_file = open(current_dir + '/upgrade_skips.txt', 'w');

freespace_dict = {};

freespace_file = open("tmp/freespace.txt","r");
with freespace_file as freespace:
    freespacedata = csv.reader(freespace)
    for row in freespacedata:
        devicename = row[0];
        fspace = row[1];
        freespace_dict[str(devicename)] = (str(fspace));

bootSystemCMDs_file = open("tmp/bootsys_cmds.txt","r");

# declare upgradeNecessary variable to track whether any devices need to be upgraded.
upgradeNecessary = 0;

with bootSystemCMDs_file as bootSystemCMDs:
    bootsysdata = csv.reader(bootSystemCMDs)
    for row in bootsysdata:
        devicename = row[0];
        current_boot_cmd = row[1];
        current_boot_image_list = current_boot_cmd.split(":");
        current_boot_image = current_boot_image_list[1];
        freespace = math.floor(float(freespace_dict[str(devicename)]));
       
        # Start playbook header
        if int(freespace) < int(options.space_required):
            print("\nThere is not enough free space to upgrade " + devicename + "\n");
            upgrade_skips_file.write("There is not enough free space to upgrade " + devicename + "\n");
        elif current_boot_image == options.new_image_file:
            print("\n" + devicename + " is already on " + options.new_image_file + "\n");
            upgrade_skips_file.write(devicename + " is already on " + options.new_image_file + "\n");
        else:
            upgradeNecessary = 1;
            playbookfile.write('- name: ' + devicename + '_pb\n');
            playbookfile.write('  hosts: ' + devicename + '\n');
            playbookfile.write('  gather_facts: ' + options.gather_facts + '\n');
            playbookfile.write('  vars:\n');
            playbookfile.write('   ansible_command_timeout: ' + str(options.ansible_command_timeout) + '\n');
            playbookfile.write('  tasks:\n');

            if hasattr(options,'revert_timer'):
                playbookfile.write('   - name: config_revert\n');
                playbookfile.write('     ' + options.cisco_command_type + ':\n');
                playbookfile.write('      commands:\n');
                if not options.archive_path == "":
                    playbookfile.write('       - configure terminal\n');
                    playbookfile.write('       - archive\n');
                    playbookfile.write("       - '" + options.archive_path + "'\n");
                    playbookfile.write('       - end\n');
                playbookfile.write('       - configure terminal revert timer ' + str(options.revert_timer) + '\n');
                playbookfile.write('       - end\n');

            # Add file copy commands if desired
            if hasattr(options,'ud_file_copy'):
                if options.ud_file_copy:
                    playbookfile.write('   - name: Copy_image_file\n');
                    playbookfile.write('     cli_command:\n');
                    playbookfile.write('       command: "' + options.copy_file_cmd + '"\n');
                    playbookfile.write('       check_all: True\n');
                    playbookfile.write('       prompt:\n');
                    playbookfile.write('         - "' + options.filename_prompt + '"\n');
                    playbookfile.write('       answer:\n');
                    playbookfile.write('         - ' + options.new_image_file + '\n');
            
            # Add boot system commands if desired.
            if hasattr(options,'ud_boot_sys_cmd'):
                if options.ud_boot_sys_cmd:
                    playbookfile.write('   - name: Set_boot_sys_cmds\n');
                    playbookfile.write('     ' + options.cisco_command_type + ':\n');
                    playbookfile.write('      commands:\n');
                    playbookfile.write('       - config terminal\n');
                    playbookfile.write('       - no boot system\n');
                    playbookfile.write('       - ' + options.new_boot_cmd + '\n');
                    playbookfile.write('       - boot system ' + current_boot_cmd + '\n');
                    playbookfile.write('       - config-register ' + options.config_register + '\n');
                    playbookfile.write('       - end \n');
                    if hasattr(options,'ud_write'):
                        if options.ud_write:
                            playbookfile.write('       - write\n');
            
            # Add reload command if defired.
            if hasattr(options,"ud_reload_in"):
                functions.promptReload(current_dir,options.ud_reload_in,scheduled_task);
                playbookfile.write('   - name: Write\n');
                playbookfile.write('     cli_command:\n');
                playbookfile.write('       command: "write"\n');
                playbookfile.write('   - name: Reload\n');
                playbookfile.write('     cli_command:\n');
                playbookfile.write('       command: "reload in ' + str(options.ud_reload_in) + '"\n');
                playbookfile.write('       check_all: True\n');
                playbookfile.write('       prompt:\n');
                playbookfile.write('         - "Confirm"\n');
                playbookfile.write('       answer:\n');
                playbookfile.write('         - "y"\n');

            # Add revert commands if desired
            if hasattr(options,'config_confirm'):
                if options.config_confirm:
                    playbookfile.write('   - name: config_confirm\n');
                    playbookfile.write('     ' + options.cisco_command_type + ':\n');
                    playbookfile.write('      commands:\n');
                    playbookfile.write('       - configure confirm\n');
                    playbookfile.write('       - write\n');

            playbookfile.write('########################################################################\n');

playbookfile.close();
upgrade_skips_file.close();

# Convert line endings if desired
if hasattr(options,"convert_pb_line_end"):
    if options.convert_pb_line_end:
        functions.convertLineEnd(current_dir,"jobiation_task.yaml");

# Confirm user is ready
functions.confirmReady(current_dir,scheduled_task);

# Create an run BASH script to run the playbook.
if upgradeNecessary == 1:
    functions.runPlaybook(current_dir,current_dir+"/jobiation_task.yaml",password_prompt,"\nRunning playbook.\n","\nPlaybook finished running.\n","playbook_results.txt",options.ansible_exe);
else:
    print("\n\nThere is nothing to do. All devices are already running " + options.new_image_file + " or do not have enough space.");

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
