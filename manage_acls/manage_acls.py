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
import os;

# Set a value os schedule_task if it is a scheduled task
scheduled_task = "NA";
if len(sys.argv) > 1:
    scheduled_task = sys.argv[1];
    sys.path.insert(1, './scheduled_tasks/'+scheduled_task);
    import options;

# Import modules
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

## Read aCLs dictionary and make variables
aclgroup = options.aCLs['aclgroup'];
declaration = options.aCLs['declaration'];
application = options.aCLs['application'];
intList = options.aCLs['interfaces'].split(",");
lastline = options.aCLs['lastline'];

# Remove the aclgroups temp directory if it exists and recreate it
if os.path.isdir("tmp/"+ aclgroup):
    shutil.rmtree("tmp/"+ aclgroup);
os.mkdir("tmp/"+ aclgroup);

# Declare temp file for ACL
standard_template = open("tmp/" + aclgroup + "/standard_template.txt", "w");

# Add commands to the temp file for removeing ACLs from interfaces and redeclare ACL.
for int in intList:
    standard_template.write(int + "\n");
    standard_template.write("no "+ application +"\n");
standard_template.write("no " + declaration + "\n");
standard_template.write(declaration + "\n");

# Read chosen template into temp file
with open("templates/"+aclgroup+".txt", 'r') as acl_template_as:
    acl_template_content = acl_template_as.read();
standard_template.write(acl_template_content);
acl_template_as.close();

# Add last line
standard_template.write(lastline+"\n");

# Add commands to the temp file for reapplying the ACL
for int in intList:
    standard_template.write(int + "\n");
    standard_template.write(application +"\n");

# Get back to priv exec
standard_template.write("end\n");

# Write config if desired
if hasattr(options, 'ma_write'):
    if options.ma_write:
        standard_template.write("write\n");

# Close the standard_template file
standard_template.close();

# Make template file for hosts that have only preadd or preadd and postadd.
if os.path.isdir("templates/"+aclgroup+"/preadds"):
    preadds = pathlib.Path("templates/"+aclgroup+"/preadds").iterdir();

    for preadd in preadds:
        hostname = str(preadd).replace("templates/"+aclgroup+"/preadds/","");

        # Declare temp file for ACL
        preadd_template = open("tmp/"+aclgroup+"/"+hostname, "w");

        # Add commands to the temp file for removeing ACL from interfaces and redeclare ACL.
        for int in intList:
            preadd_template.write(int + "\n");
            preadd_template.write("no "+ application +"\n");
        preadd_template.write("no " + declaration + "\n");
        preadd_template.write(declaration + "\n");

        # Read preadd file into template
        with open(preadd, 'r') as preadd_as:
            preadd_content = preadd_as.read();
        preadd_template.write(preadd_content);
        preadd_as.close();

        # Read chosen template into temp file
        preadd_template.write(acl_template_content);

        # Check if postadd exists for the same host
        if os.path.isfile("templates/"+aclgroup+"/postadds/"+hostname):
            with open("templates/"+aclgroup+"/postadds/"+hostname, 'r') as postadd_as:
                postadd_content = postadd_as.read();
            preadd_template.write(postadd_content);
            postadd_as.close();

        # Add last line
        preadd_template.write(lastline+"\n");

        # Add commands to the temp file for reapplying the ACL
        for int in intList:
            preadd_template.write(int + "\n");
            preadd_template.write(application +"\n");

        # Get back to priv exec
        preadd_template.write("end\n");

        # Write config if desired
        if hasattr(options, 'ma_write'):
            if options.ma_write:
                preadd_template.write("write\n");

        # Close the temp file
        preadd_template.close();

# Make template file for hosts that have only postadd.
if os.path.isdir("templates/"+aclgroup+"/postadds"):
    postadds = pathlib.Path("templates/"+aclgroup+"/postadds").iterdir();

    for postadd in postadds:
        hostname = str(postadd).replace("templates/"+aclgroup+"/postadds/","");

        # Check if template file was already created by the preadd block
        if os.path.isfile("tmp/"+aclgroup+"/"+hostname):
            print("");
        else:
            # Declare temp file for ACL
            postadd_template = open("tmp/"+aclgroup+"/"+hostname, "w");

            # Add commands to the temp file for removeing ACL from interfaces and redeclare ACL.
            for int in intList:
                postadd_template.write(int + "\n");
                postadd_template.write("no "+ application +"\n");
            postadd_template.write("no " + declaration + "\n");
            postadd_template.write(declaration + "\n");

            # Read chosen template into temp file
            postadd_template.write(acl_template_content);

            # Read preadd file into template
            with open(postadd, 'r') as postadd_as:
                postadd_content = postadd_as.read();
            postadd_template.write(postadd_content);
            postadd_as.close();

            # Add last line
            postadd_template.write(lastline+"\n");

            # Add commands to the temp file for reapplying the ACL
            for int in intList:
                postadd_template.write(int + "\n");
                postadd_template.write(application +"\n");

            # Get back to priv exec
            postadd_template.write("end\n");

            # Write config if desired
            if hasattr(options, 'ma_write'):
                if options.ma_write:
                    postadd_template.write("write\n");

            # Close the temp file
            postadd_template.close();

# Ask user if they want to do a write and reload
if hasattr(options, 'ma_reload_in'):
    functions.promptReload(current_dir,options.ma_reload_in,scheduled_task);

# Make a list of the first line columns of inventory.csv
flList = functions.getFirstLine(open(options.inventory_file,"r"));

# Make sure flList has required columns
functions.validateReqCol(req_columns,flList);

# Get index value of devicename
devicenameIndex = functions.getListIndex(flList,"devicename");

# Validate devicename column
functions.validateDevicename(open(options.inventory_file,"r"),validations.devicenameAllowed,current_dir,messages.badDeviceName,devicenameIndex);

# Open acl template and cache in variable acl_template
with open("tmp/"+ aclgroup +"/standard_template.txt", "r") as acl_temp:
    acl_template = acl_temp.read();
acl_temp.close();

# Validate the first line of inventory.csv
functions.validateFirstLine(flList,current_dir,messages.badFirstLine);

#Make spaces variable
spaces = "        ";

# Build Hosts header if use_hosts_header == False
if(options.use_hosts_header == False):
    functions.makeHostsHeader(current_dir,options.ansible_python_interpreter,options.ansible_connection,options.ansible_network_os,options.ansible_port,username,become_necessary);

# Make temp python file
tempfile = open("tmp/tempfile.py","w");

# Add shebang and imports to tempfile.py
tempfile.write("#!/usr/bin/env python3\n");
tempfile.write("import csv\n");
tempfile.write("import os\n");

# Write ACL group to the temp file
tempfile.write("aclgroup = '"+ aclgroup +"';\n");

# Open files in tempfile.py
tempfile.write("hostsfile = open('" + current_dir + "/hosts.yaml', 'a+');\n");
tempfile.write("inventoryfile = open('"+options.inventory_file+"', 'r');\n");
tempfile.write("playbookfile = open('" + current_dir + "/jobiation_task.yaml', 'w');\n");
tempfile.write("playbookfile.write('---\\n');\n");

# Interate through inventory file
tempfile.write("with inventoryfile as invfile:\n");
tempfile.write("    invdata = csv.reader(invfile)\n");
tempfile.write("    for row in invdata:\n");

# Make a list for variables used
vars_used = [];

# Open host_conditions.py and cache in variable hostcond_content
with open(options.host_conditions_file, 'r') as hostcond_file:
    hostcond_content = hostcond_file.read();
hostcond_file.close();

# Add required columns, columns used in host_conditions.py, columns used in the aCLs dictionary, and columns used in the acl template to tempfile.py
for flCol in range(len(flList)-1):
    if flList[flCol] in req_columns:
        tempfile.write("        "+flList[flCol]+" = row["+str(flCol)+"];\n");
        if re.search("!"+flList[flCol]+"!", acl_template):
            vars_used.append(flList[flCol]);
    elif re.search("!"+flList[flCol]+"!", acl_template):
        tempfile.write("        "+flList[flCol]+" = row["+str(flCol)+"];\n");
        vars_used.append(flList[flCol]);
    elif re.search("str\\(" + flList[flCol] + "\\)", hostcond_content):
        tempfile.write("        "+flList[flCol]+" = row["+str(flCol)+"];\n"); # This line is necessary for variables used in host_conditions.py

# Add hosts_conditions.py to tempfile.py
tempfile.write(hostcond_content);

# Add commands for hosts file to tempfile.py
tempfile.write(spaces + "hostsfile.write('       ' + devicename + ':\\n');\n");
tempfile.write(spaces + "hostsfile.write('         ansible_host: ' + ip + '\\n');\n");

# Add commands to playbook file
tempfile.write(spaces + "playbookfile.write('- name: ' + devicename + '_pb\\n');\n");
tempfile.write(spaces + "playbookfile.write('  hosts: ' + devicename + '\\n');\n");
tempfile.write(spaces + "playbookfile.write('  gather_facts: "+options.gather_facts+"\\n');\n");
tempfile.write(spaces + "playbookfile.write('  vars:\\n');\n");
tempfile.write(spaces + "playbookfile.write('   ansible_command_timeout: "+str(options.ansible_command_timeout)+"\\n');\n");
tempfile.write(spaces + "playbookfile.write('  tasks:\\n');\n");

# Add write and reload if desired
if hasattr(options, 'ma_reload_in'):
    functions.reloadIn(tempfile,options.ma_reload_in,spaces);

# Add revert commands if desired
if hasattr(options,'revert_timer'):
    functions.setRevertTimer(tempfile,spaces,options.cisco_command_type,options.revert_timer,options.archive_path);

# Add playbook header commands to tempfile.py
tempfile.write(spaces + "playbookfile.write('   - name: ' + devicename + '_commands\\n');\n");
tempfile.write(spaces + "playbookfile.write('     " + options.cisco_command_type + ":\\n');\n");
tempfile.write(spaces + "playbookfile.write('      commands:\\n');\n");
tempfile.write(spaces + "playbookfile.write('       - configure terminal\\n');\n");

# Add commands for variable replacement
tempfile.write(spaces + "if os.path.isfile('tmp/'+aclgroup+'/'+devicename+'.txt'):\n");
tempfile.write(spaces + "    commandsfile = open('tmp/'+aclgroup+'/'+devicename+'.txt', 'r');\n");
tempfile.write(spaces + "else:\n");
tempfile.write(spaces + "    commandsfile = open('tmp/" + aclgroup + "/standard_template.txt', 'r');\n");
tempfile.write(spaces + "for cmd in commandsfile:\n");
tempfile.write(spaces + "    repstr = cmd;\n");

# Make replacements
for replacement in vars_used:
    tempfile.write(spaces + "    repstr = repstr.replace('!"+replacement+"!', "+replacement+");\n");
tempfile.write(spaces + "    playbookfile.write('       - ' + repstr);\n");

# Close commandsfile
tempfile.write(spaces + "commandsfile.close();\n");

# Confirm config if desired
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

# Close temp file
tempfile.close();

# Execute tempfile.py
os.chmod("tmp/tempfile.py", 0o770);
exec(open("tmp/tempfile.py").read());

# Remove the aclgroups temp directory.
if os.path.isdir("tmp/"+ aclgroup):
    shutil.rmtree("tmp/"+ aclgroup);

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