#!/usr/bin/env python3
import csv
import sys
import shutil
import os
inventoryfile = open('../inventory.csv', 'w+');
with inventoryfile as invfile:
    invdata = csv.reader(invfile)
    for row in invdata:
        devicename = row[0];
        active = row[1];
        ip = row[2];
        arg3 = row[7];
# Note that 'continue' means skip.
# Conditions must be casted as strings
# Conditions form a logical AND

        if str(arg3) != '1':
            continue;

        if str(active) != '1':
            continue;

        if str(devicename) == 'devicename':
            continue;

        if str(devicename) == 'skipline':
            continue;
        with open(jobs/20221207_1658+'/'+devicename+'.txt', 'r') as showcmdfile:
            filecontent = showcmdfile.read();
        match = re.search('GigabitEthernet0/0/0',filecontent)
