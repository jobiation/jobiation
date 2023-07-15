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
# import shutil;
import os;
from datetime import datetime;
import re;

# Import options and functions modules
sys.path.insert(1, '../');
import options;
import functions;
import validations;
import messages;

# Check argument and set commands_file variable
if len(sys.argv) > 1:
    commands_file = sys.argv[1];
else:
    print("This script requires an argument specifying a template file.");
    sys.exit();

# Validate the task name
functions.validateArg(validations.argNameAllowed,commands_file,messages.badArgNameMsg);

# Make array of required columns
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

# Open commands file and cache in variable commands_content
with open(commands_file, 'r') as commands:
    commands_content = commands.read();
commands.close();

# Validate the first line of inventory.csv
functions.validateFirstLine(flList,current_dir,messages.badFirstLine);

#Make spaces variable
spaces = "        ";

# Make temp python file
tempfile = open("tmp/tempfile.py","w");

# Add shebang and imports to tempfile.py
tempfile.write("#!/usr/bin/env python3\n");
tempfile.write("import csv\n");

tempfile.write("current_dir = '"+current_dir+"';\n");
tempfile.write("inventoryfile = open('"+options.inventory_file+"', 'r');\n");

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

# Add commands for variable replacement
tempfile.write(spaces+"commandsfile = open('"+commands_file+"', 'r');\n");

tempfile.write(spaces+"templatefile = open(current_dir+'/'+devicename+'.txt', 'w');\n");

tempfile.write(spaces + "for cmd in commandsfile:\n");
tempfile.write(spaces + "    repstr = cmd;\n");

# Make replacements
for replacement in vars_used:
    tempfile.write(spaces + "    repstr = repstr.replace('!"+replacement+"!', "+replacement+");\n");
tempfile.write(spaces + "    templatefile.write(repstr);\n");
tempfile.write(spaces + "templatefile.write('\\n');\n");
tempfile.write(spaces + "templatefile.close();");
tempfile.write("\n");
tempfile.write(spaces + "commandsfile.close();");

# Add commands to tempfile.py to close all files.
tempfile.write("\n");
tempfile.write("inventoryfile.close();\n");

# Close temp file
tempfile.close();

# # Execute tempfile.py
os.chmod("tmp/tempfile.py", 0o770);
exec(open("tmp/tempfile.py").read());

# Notify user playbook has finished
print("\nScript has finished running.\n");