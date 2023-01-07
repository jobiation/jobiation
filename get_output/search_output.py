#!/usr/bin/env python3

# Imports
import sys # For exiting the script early with sys.exit();
from datetime import datetime
import re
import pathlib
import os

# Import options file
sys.path.insert(1, '../');
import options
import functions

# Get current date and time
now = datetime.now() # current date and time
date_time = now.strftime("%Y%m%d_%H%M");

# Ask the user to pick the directory to search
dirs = [];
jobs_dir = pathlib.Path("jobs").iterdir();
for dir in jobs_dir:
    dirs.append(str(dir));
if len(dirs) == 0:
    print("There are no jobs to search. Please run get_output so there will be some output to search.");
    sys.exit();
dirs_count = 0;
dirs.sort(reverse=True);
for dir in dirs:
    dirs_count = dirs_count + 1;
    if dirs_count <= 5:
        print("[" + str(dirs.index(dir)) + "]" + dir);
dir_choice = input("Type the number of the directory you want to search: ");
current_dir = str(dirs[int(dir_choice)]);

# Declare hosts list
hosts = [];

# Declare a list to hold all the records in the file
fileList = ["host,"];

# Open hosts file in the chosen directory
hostsfile = open(current_dir+"/hosts","r");

# Populate hosts list
hostsvarfound = 0;
evenodd = 0;
for host in hostsfile:
    if hostsvarfound == 1:
        if evenodd == 0:
            evenodd = 1;
            hosts.append(host.strip().replace(':',''));
            fileList.append(host.strip().replace(':',','));
        else:
            evenodd = 0;
    if "hosts:" in host:
        hostsvarfound = 1;
hostsfile.close();

# Iterate searches[]
dictAllowedChars =re.compile("^[a-z]([a-z]?[A-Z]?[0-9]?_?){1,14}$");
for search in options.searches:
    if re.search(dictAllowedChars, search):
        searchinfo = options.searches[search].split("!!");
        searchdir = searchinfo[0];
        searchdetail = searchinfo[1];
    else:
        functions.abortPlaybook(current_dir,"Please only use letters, numbers, and underscores for the keys of the searches dictionary. Keep it under 15 characters. The first character should be a lower case letter.");


    fileList[0] = fileList[0]+search+",";

    #Iterate hosts[]
    for host in hosts:
        if os.path.isfile(current_dir+'/'+searchdir+'/'+host+'_'+searchdir+'.txt'):
            with open(current_dir+'/'+searchdir+'/'+host+'_'+searchdir+'.txt', 'r') as outputfile:
                content = outputfile.read();
            match = re.search(searchdetail, content)
            if match:
                fileList[hosts.index(host)+1] = fileList[hosts.index(host)+1]+"1,";
            else:
                fileList[hosts.index(host)+1] = fileList[hosts.index(host)+1]+"0,";
        else:
            fileList[hosts.index(host)+1] = fileList[hosts.index(host)+1]+"NA,";


# Declare report file
reportfile = open(current_dir+"/report_"+date_time+".csv","w");

# Populate report file
for hostrecord in fileList:
    reportfile.write(hostrecord+"\n");
    print(hostrecord);

# Close report file
reportfile.close();