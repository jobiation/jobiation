#!/usr/bin/env python3

import csv
import sys
import shutil
import os

hostsfile = open("tmp/hosts", "a+");
playbookfile = open("jobiation_task.yaml", "w+");
playbookfile.write("---\n");
inventoryfile = open("../inventory.csv", "r");
commandsfile = open("commands.txt", "r");

with inventoryfile as csvfile:
    datareader = csv.reader(csvfile)
    for row in datareader:
        devicename = row[0];
        active = row[1];
        ip = row[2];
        arg1 = row[5];
        arg2 = row[6];
# Note that continue means skip.

        if str(arg1) != "1":
            continue;

        if str(active) != "1":
            continue;

        if str(devicename) == "devicename":
            continue;

        if str(devicename) == "skipline":
            continue;

        hostsfile.write("       " + devicename + ":\n");
        hostsfile.write("         ansible_host: " + ip + "\n");

        playbookfile.write("- name: " + devicename + "_pb\n");
        playbookfile.write("  hosts: " + devicename + "\n");
        playbookfile.write("  gather_facts: no\n");
        playbookfile.write("  vars:\n");
        playbookfile.write("    ansible_command_timeout: 30\n");
        playbookfile.write("  tasks:\n");
        playbookfile.write("  - name: " + devicename + "_commands\n");
        playbookfile.write("    ios_commands:\n");
        playbookfile.write("      commands:\n");
        for cmd in commandsfile:
            repstr = cmd;
            repstr = repstr.replace('!devicename', devicename);
            repstr = repstr.replace('!arg1', arg1);
            repstr = repstr.replace('!arg2', arg2);
            playbookfile.write('        - ' + repstr);
inventoryfile.close();
hostsfile.close();
playbookfile.close();
commandsfile.close();