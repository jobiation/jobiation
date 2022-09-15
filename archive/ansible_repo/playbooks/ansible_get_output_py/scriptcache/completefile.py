#!/usr/bin/env python3

import csv
import sys
import shutil
import os

hostsfile = open("/var/ansiblerepo/playbooks/ansible_get_output_py/hosts", "a+");
# playbookfile = open("/var/ansiblerepo/playbooks/ansible_get_output_py/ansible_task.yaml", "w+");
# playbookfile.write("---\n");
devicesfile = open("/var/ansiblerepo/playbooks/ansible_get_output_py/ansibledevices.csv", "r");
with devicesfile as csvfile:
    datareader = csv.reader(csvfile)
    for row in datareader:
        devicename = row[0];
        active = row[1];
        ip = row[2];
        location = row[3];
        model = row[4];
        arg1 = row[5];
        arg2 = row[6];
        arg3 = row[7];
        aclgrp = row[8];
        aclname = row[9];
        aclsub1 = row[10];
        aclsub2 = row[11];
        aclint1 = row[12];
        aclint1dir = row[13];
        aclint2 = row[14];
        aclint2dir = row[15];
        aclpostadd = row[16];
        aclpreadd = row[17];
        acllastcmd = row[18];
        if str(arg1) == "1":
            print("arg1 is 1");

        if str(devicename) == "devicename":
            continue;

        if str(devicename) == "skipline":
            continue;

        if str(active) != "1":
            continue;

        print(devicename);

        hostsfile.write("       " + devicename + ":\n");
        hostsfile.write("         ansible_host: " + ip + "\n");

# Close files
# playbookfile.close();
devicesfile.close();
hostsfile.close();