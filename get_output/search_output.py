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
from datetime import datetime;
import re;
import pathlib;
import os;

# Import options file
sys.path.insert(1, '../');
import options;
import functions;
import validations;
import messages;

# Get current date and time
now = datetime.now() # current date and time
date_time = now.strftime("%Y%m%d_%H%M");

# Ask the user to pick the directory to search
dirs = [];
jobs_dir = pathlib.Path("jobs").iterdir();
for dir in jobs_dir:
    dirs.append(str(dir));
if len(dirs) == 0:
    print("\nThere are no jobs to search. Please run get_output.py so there will be some output to search.\n");
    sys.exit();
dirs_count = 0;
dirs.sort(reverse=True);
for dir in dirs:
    dirs_count = dirs_count + 1;
    if dirs_count <= 5:
        print("[" + str(dirs.index(dir)) + "]" + dir);
dir_choice = input("\nType the number of the directory you want to search: ");
current_dir = str(dirs[int(dir_choice)]);

# Declare hosts list
hosts = [];

# Declare a list to hold all the records in the file
fileList = ["host,"];

# Open hosts file in the chosen directory
hostsfile = open(current_dir+"/hosts.yaml","r");

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

# Iterate searches[], validate keys, and split by !!
for search in options.searches:
    if re.search(validations.dictAllowedChars, search):
        searchinfo = options.searches[search].split("!!");
        searchdir = searchinfo[0];
        filetype = searchinfo[1];
        searchdetail = searchinfo[2];
    else:
        functions.abortPlaybook(current_dir,"\n!"+search+messages.badDictKey,False);

    fileList[0] = fileList[0]+search+",";

    #Iterate hosts[] and match hosts that match the user specified condition
    for host in hosts:
        if os.path.isfile(current_dir+'/'+searchdir+'/'+host+'_'+searchdir+filetype):
            with open(current_dir+'/'+searchdir+'/'+host+'_'+searchdir+filetype, 'r') as outputfile:
                content = outputfile.read();
            match = re.search(searchdetail, content)
            if match:
                fileList[hosts.index(host)+1] = fileList[hosts.index(host)+1]+"1,";
            else:
                fileList[hosts.index(host)+1] = fileList[hosts.index(host)+1]+"0,";
        else:
            fileList[hosts.index(host)+1] = fileList[hosts.index(host)+1]+"NA,";


# Create report file
reportfile = open(current_dir+"/search_report_"+date_time+".csv","w");

# Populate report file
for hostrecord in fileList:
    reportfile.write(hostrecord+"\n");

# Close report file
reportfile.close();

# Notify user the report is ready
print("\nCheck " + current_dir+"/search_report_"+date_time+".csv for your search results.\n");