#!/usr/bin/env python3

# Imports
import csv
import sys # For exiting the script early with sys.exit();
import shutil # For copyfile
import os # For mkdir
from datetime import datetime
import subprocess # For running a bash script
import re
import pathlib

# Make list of required columns
req_columns = [ "devicename", "ip", "active" ];

# Import options file
sys.path.insert(1, '../');
import options

# Import gofunctions file
import gofunctions

# Get current date and time
now = datetime.now() # current date and time
date_time = now.strftime("%Y%m%d_%H%M");

# Declare variables from options files
facts_export = 0;
showcmd_exports = 0;
searches = 0;

# Set facts_export variable
if hasattr(options, 'facts_export'):
    facts_export = 1;

# Set showcnd_exports variable
if len(options.showcmd_exports) >= 1:
    showcmd_exports = 1;

# Set searches variable
if len(options.searches) >= 1:
    searches = 1;

# Check if there is anything to do
if facts_export == 0 and showcmd_exports == 0 and searches == 0:
    print("facts_export is not set, showcmd_exports is null, and searches is null so there is nothing to do. Please check options.py.");
    sys.exit();

# Check if the job is search only.
if facts_export == 0 and showcmd_exports == 0 and searches == 1:
    dirs = [];
    jobs_dir = pathlib.Path("jobs").iterdir();
    for dir in jobs_dir:
        dirs.append(str(dir));
    if len(dirs) == 0:
        print("There are no jobs to search. Please open options.py and uncomment facts_export or add at least one item to the showcmd_exports dictionary.");
        sys.exit();
    dirs_count = 0;
    dirs.sort(reverse=True);
    for dir in dirs:
        dirs_count = dirs_count + 1;
        if dirs_count <= 5:
            print("[" + str(dirs.index(dir)) + "]" + dir);
    dir_choice = input("Type the number of the directory you want to search: ");
    current_dir = str(dirs[int(dir_choice)]);
else:
    # # Make a directory for the job
    current_dir = "jobs/" + date_time;
    os.mkdir(current_dir);

    print("Working directory is " + current_dir);

    # Copy hosts_header or check if username is needed in the options file
    password_prompt = " -k";

    if(options.use_hosts_header == 1):
        if not os.path.exists("../hosts_header"):
            input("You need to put a hosts_header file in the jobiation root when you set the use_hosts_header to 1 in options.py.");
            sys.exit();
        shutil.copyfile("../hosts_header", current_dir + "/hosts");
        username = "NA";
        password_prompt = "";
    elif(options.ansible_user == ""):
        username = input("You do not have a username set. What username do you want to use? ");
    else:
        username = options.ansible_user;

    # open inventory.csv
    inventoryfile = open("../inventory.csv","r");

    # Make a list of the first line
    with inventoryfile as invrow:
        firstline = invrow.readline();
    flList = firstline.split(",");

    # Close the inventory file
    inventoryfile.close();

    # Validate the first line of inventory.csv
    flAllowedChars =re.compile("^([0-9]?[a-z]?[A-Z]?_?){1,15}$");
    for flCol in range(len(flList)-1):
        if not re.search(flAllowedChars, str(flList[flCol])):
            print(flList[flCol] + " contains an illegal character.\n\nThe top line of the inventory can contain numbers, letters, and underscores.\n\nAlso, please do not use more than 15 characters in any one column header.");
            sys.exit();

    # Build Hosts header if use_hosts_header == 0
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
    tempfile.write("playbookfile.write('   ansible_command_timeout: "+options.ansible_command_timeout+"\\n');\n");
    tempfile.write("playbookfile.write('  tasks:\\n');\n");

    # Save facts if desired
    if hasattr(options, 'facts_export'):
        os.mkdir(current_dir+"/facts");
        gofunctions.saveFacts(tempfile,options.facts_export,current_dir);

    # save output from show command if desired.
    if len(options.showcmd_exports) >= 1:
        for cmd in options.showcmd_exports:
            os.mkdir(current_dir+"/"+cmd);
            gofunctions.saveShowCmd(tempfile,options.cisco_product_line,options.showcmd_exports[cmd],cmd,current_dir);

    tempfile.write("with inventoryfile as invfile:\n");
    tempfile.write("    invdata = csv.reader(invfile)\n");
    tempfile.write("    for row in invdata:\n");

    # Open host_conditions.py and cache in variable hostcond_content
    with open('../host_conditions.py', 'r') as hostcond_file:
        hostcond_content = hostcond_file.read();

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

    confirm_ready = input("-- Your playbook and hosts file is ready.\n\n-- Please open them in " + current_dir + ".\n\n-- Make sure the commands are the commands you intend to perform on your Cisco devices.\n\n-- Press ENTER when ready.");
    if(confirm_ready != ""):
        print("Aborting!");
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
    with open(current_dir + "/hosts", "w") as hosts:
        for hostsline in hostslines:
            matchuser = re.search('ansible_user', hostsline)
            matchpass = re.search('ansible_password', hostsline)
            if matchuser and options.remove_username == 1:
                print("\n\nRemoving username from hosts file.\n\n");
            elif matchpass and options.remove_password == 1:
                print("\n\nRemoving password from hosts file.\n\n");
            else:
                hosts.write(hostsline);

    # Remove the hosts_header file if desired
    if(options.remove_hosts_header == 1):
        if os.path.exists("../hosts_header"):
            os.remove("../hosts_header");


######################### Search #############################

print("You made it to the search section");
sys.exit();


# Make temp python file
tempfile2 = open("tmp/tempfile2.py","w");

# Add shebang and imports to tempfile.py
tempfile2.write("#!/usr/bin/env python3\n");
tempfile2.write("import csv\n");
tempfile2.write("import sys\n");
tempfile2.write("import shutil\n");
tempfile2.write("import os\n");

# Open files in tempfile.py
tempfile2.write("inventoryfile = open('../inventory.csv', 'w+');\n");

tempfile2.write("with inventoryfile as invfile:\n");
tempfile2.write("    invdata = csv.reader(invfile)\n");
tempfile2.write("    for row in invdata:\n");

# Open host_conditions.py and cache in variable hostcond_content
with open('../host_conditions.py', 'r') as hostcond_file:
    hostcond_content = hostcond_file.read();

# Add required columns and columns used in host_conditions.py
for flCol in range(len(flList)-1):
    if flList[flCol] in req_columns:
        tempfile2.write("        "+flList[flCol]+" = row["+str(flCol)+"];\n");
    elif re.search("str\\(" + flList[flCol] + "\\)", hostcond_content):
        tempfile2.write("        "+flList[flCol]+" = row["+str(flCol)+"];\n"); # This line is necessary for variables used in host_conditions.py

# Add hosts_conditions.py to tempfile.py
tempfile2.write(hostcond_content);

tempfile2.write("        with open(" + current_dir + "+'/'+devicename+'.txt', 'r') as showcmdfile:\n");
tempfile2.write("            filecontent = showcmdfile.read();\n");
tempfile2.write("        match = re.search('" + options.search_showcmd + "',filecontent)\n");
# tempfile.write("        \n");


# with open('.txt', 'r') as showcmdfile:
#     content = showcmdfile.read();
# match = re.search('(interface GigabitEthernet0/0/0(.*\n){1,3}ip address)(.*\n){1,6}interface GigabitEthernet0/0/1', content)
# if match:
#   print("match");
# else:
#   print("no match");

# Close tempfile2.py
tempfile2.close();
