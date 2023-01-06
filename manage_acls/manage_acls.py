#!/usr/bin/env python3

# Imports
import sys # For exiting the script early with sys.exit();
import shutil # For copyfile
import os # For mkdir
from datetime import datetime
import subprocess # For running a bash script
import re
import pathlib
import os

# Make array of required columns
req_columns = [ "devicename", "ip", "active" ];

# Import options file
sys.path.insert(1, '../');
import options
import functions

# Import send_command_functions
import mafunctions

# Get current date and time
now = datetime.now() # current date and time
date_time = now.strftime("%Y%m%d_%H%M");

# # Make a directory for the job
if os.path.isdir('jobs/' + date_time):
    print("You cannot run more than one job within the same minute. Please wait until the end of this minute and try again.");
else:
    os.mkdir('jobs/' + date_time);
    current_dir = "jobs/" + date_time;


# Copy hosts_header or check if username is needed in the options file
password_prompt = " -k";

if(options.use_hosts_header == True):
    if not os.path.exists("../hosts_header"):
        input("You need to put a hosts_header file in the jobiation root when you set the use_hosts_header to True in options.py.");
        sys.exit();
    shutil.copyfile("../hosts_header", current_dir + "/hosts");
    username = "NA";
    password_prompt = "";
elif(options.ansible_user == ""):
    username = input("You do not have a username set. What username do you want to use? ");
else:
    username = options.ansible_user;

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

# Add commands to the temp file for removeing ACL from interfaces and redeclare ACL.
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

# Close the temp file
standard_template.close();

# Make template file for hosts that have only preadd or pre and postadd.
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

    # Check if post add exists for the same host
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

    # Close the temp file
    preadd_template.close();

# Make template file for hosts that have only preadd or pre and postadd.
postadds = pathlib.Path("templates/"+aclgroup+"/postadds").iterdir();

for postadd in postadds:
    hostname = str(postadd).replace("templates/"+aclgroup+"/postadds/","");

    # Check if template file was already created by the preadd block
    if os.path.isfile("tmp/"+aclgroup+"/"+hostname):
        print("post add file already created for " + hostname);
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

        # Close the temp file
        postadd_template.close();

# Ask user if they want to do a write and reload
if hasattr(options, 'reload_in'):
    confirm_reload = input("ATTENTION! You have the reload_in option enabled.\n\nYour specified devices will be reloaded in " + str(options.reload_in) + " minutes.\n\nType 'yes' if you want to continue or press ENTER to cancel. ");
    if confirm_reload.lower() != "yes":
        print("Aborting!");
        sys.exit();

# Open acl template and cache in variable acl_template
with open("tmp/"+ aclgroup +"/standard_template.txt", "r") as acl_temp:
    acl_template = acl_temp.read();

# open inventory.csv
inventoryfile = open("../inventory.csv","r");

# Make a list of the first line
with inventoryfile as invrow:
    firstline = invrow.readline()
flList = firstline.split(",");

# Close the inventory file
inventoryfile.close();

# Validate the first line.
flAllowedChars =re.compile("^([0-9]?[a-z]?[A-Z]?_?){1,15}$");
for flCol in range(len(flList)-1):
    # if re.search("!"+flList[flCol]+"!", acl_template):
    #     replacements_required = replacements_required+1;
    if not re.search(flAllowedChars, str(flList[flCol])):
        print(flList[flCol] + " contains an illegal character.\n\nThe top line of the inventory can contain numbers, letters, and underscores.\n\nAlso, please do not use more than 15 characters in any one column header.");
        sys.exit();

spaces = "        ";

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
tempfile.write("import os\n");

# Write ACL group to the temp file
tempfile.write("aclgroup = '"+ aclgroup +"';\n");

# Open files in tempfile.py
tempfile.write("hostsfile = open('" + current_dir + "/hosts', 'a+');\n");
tempfile.write("inventoryfile = open('../inventory.csv', 'r');\n");
# tempfile.write("standard_commandsfile = open('tmp/" + aclgroup + "/standard_template.txt', 'r');\n");
tempfile.write("playbookfile = open('" + current_dir + "/jobiation_task.yaml', 'w');\n");
tempfile.write("playbookfile.write('---\\n');\n");

tempfile.write("with inventoryfile as invfile:\n");
tempfile.write("    invdata = csv.reader(invfile)\n");
tempfile.write("    for row in invdata:\n");

# Make a list for variables used
vars_used = [];

# Open host_conditions.py and cache in variable hostcond_content
with open('../host_conditions.py', 'r') as hostcond_file:
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
if hasattr(functions, 'reload_in'):
    mafunctions.reloadIn(tempfile,options.reload_in,spaces);

# Add commands to tempfile.py
tempfile.write(spaces + "playbookfile.write('   - name: ' + devicename + '_commands\\n');\n");
tempfile.write(spaces + "playbookfile.write('     " + options.cisco_product_line + ":\\n');\n");
tempfile.write(spaces + "playbookfile.write('      commands:\\n');\n");

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

# Make line between devices for easier reading.
tempfile.write(spaces + "playbookfile.write('\\n###############################################################\\n');\n");

# Add commands to tempfile.py to close all files.
tempfile.write("\n");
tempfile.write("inventoryfile.close();\n");
tempfile.write("hostsfile.close();\n");
tempfile.write("playbookfile.close();\n");
# tempfile.write("standard_commandsfile.close();");

# Close temp file
tempfile.close();

# Execute tempfile.py
os.chmod("tmp/tempfile.py", 0o770);
exec(open("tmp/tempfile.py").read());

# Remove the aclgroups temp directory if it exists and recreate it
shutil.rmtree("tmp/"+ aclgroup);

confirm_ready = input("Your playbook and hosts file is ready.\n\nPlease open them in " + current_dir + ".\n\nMake sure the commands are the commands you intend to perform on your Cisco devices.\n\nPress ENTER when ready.");
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
        if matchuser and options.remove_username == True:
            print("\n\nRemoving username from hosts file.\n\n");
        elif matchpass and options.remove_password == True:
            print("\n\nRemoving password from hosts file.\n\n");
        else:
            hosts.write(hostsline);

# Remove the hosts_header file if desired
if(options.remove_hosts_header == True):
    if os.path.exists("../hosts_header"):
        os.remove("../hosts_header");
