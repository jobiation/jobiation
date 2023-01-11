#!/usr/bin/env python3

# Imports
import sys;
import shutil;
import os;
from datetime import datetime;
import subprocess;
import re;
import pathlib;

# Make list of required columns
req_columns = [ "devicename", "ip", "active" ];

# Import options and functions modules
sys.path.insert(1, '../');
import options;
import functions;

# Import gofunctions modules
import gofunctions;

# Make sure required directories exist
if not os.path.isdir('jobs'):
    os.mkdir('jobs');
if not os.path.isdir('tmp'):
    os.mkdir('tmp');

# Make a list of the first line columns of inventory.csv
flList = functions.getFirstLine(open("../inventory.csv","r"));

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

# Declare variables from options files
facts_export = 0;
showcmd_exports = 0;

# Set facts_export variable
if hasattr(options, 'facts_export'):
    facts_export = 1;

# Set showcnd_exports variable
if len(options.showcmd_exports) >= 1:
    showcmd_exports = 1;

# Check if there is anything to do
if facts_export == 0 and showcmd_exports == 0:
    print("\nfacts_export is not set and showcmd_exports is null so there is nothing to do. Please check options.py.\n");
    shutil.rmtree(current_dir);
    sys.exit();

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

# Validate the first line of inventory.csv
flAllowedChars =re.compile("^([0-9]?[a-z]?[A-Z]?_?){1,14}$");
for flCol in range(len(flList)-1):
    if not re.search(flAllowedChars, str(flList[flCol])):
        print("\n"+flList[flCol] + " contains an illegal character.\n\nThe top line of the inventory can contain numbers, letters, and underscores.\n\nAlso, please do not use more than 15 characters in any one column header.\n");
        shutil.rmtree(current_dir);
        sys.exit();

# Build Hosts header if use_hosts_header == False
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
if hasattr(options, 'facts_export'):
    os.mkdir(current_dir+"/facts");
    gofunctions.saveFacts(tempfile,options.facts_export,current_dir);

# save output from show command if desired and validate user defined dictionary
dictAllowedChars =re.compile("^[a-z]([a-z]?[A-Z]?[0-9]?_?){1,14}$");
if len(options.showcmd_exports) >= 1:
    for subdir in options.showcmd_exports:
        if re.search(dictAllowedChars, subdir):
            os.mkdir(current_dir+"/"+subdir);
            gofunctions.saveShowCmd(tempfile,options.cisco_product_line,options.showcmd_exports[subdir],subdir,current_dir);
        else:
            functions.abortPlaybook(current_dir,"Please only use letters, numbers, and underscores for the keys of the searches dictionary. Keep it under 15 characters. The first character should be a lower case letter.");

# Interate through inventory file
tempfile.write("with inventoryfile as invfile:\n");
tempfile.write("    invdata = csv.reader(invfile)\n");
tempfile.write("    for row in invdata:\n");

# Open host_conditions.py and cache in variable hostcond_content
with open('../host_conditions.py', 'r') as hostcond_file:
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

# Remove sensitive data
dirs = options.commands_to_remove;

for dir in dirs:
    if re.search(dictAllowedChars, dir):
        cmds_to_remove = str(dirs[dir]);
        subdirlist = pathlib.Path(current_dir+"/"+dir).iterdir();
        for cmdfile in subdirlist:
            gofunctions.cleanFile(cmdfile,cmds_to_remove);
