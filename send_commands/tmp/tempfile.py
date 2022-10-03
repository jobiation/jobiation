#!/usr/bin/env python3
import csv
import sys
import shutil
import os
hostsfile = open('jobs/20221001_2107/hosts', 'a+');
inventoryfile = open('../inventory.csv', 'r');
commandsfile = open('commands.txt', 'r');
playbookfile = open('jobs/20221001_2107/jobiation_task.yaml', 'w');
playbookfile.write('---\n');
playbookfile.write('- name: jobiation_pb\n');
playbookfile.write('  hosts: jobiation_inventory\n');
playbookfile.write('  gather_facts: no\n');
playbookfile.write('  vars:\n');
playbookfile.write('   ansible_command_timeout: 30\n');
playbookfile.write('  tasks:\n');
playbookfile.write('   - name: Write\n');
playbookfile.write('     cli_command:\n');
playbookfile.write('       command: "write"\n');
playbookfile.write('   - name: Reload\n');
playbookfile.write('     cli_command:\n');
playbookfile.write('       command: "reload in 60"\n');
playbookfile.write('       check_all: True\n');
playbookfile.write('       prompt:\n');
playbookfile.write('         - "Confirm"\n');
playbookfile.write('       answer:\n');
playbookfile.write('         - "y"\n');
playbookfile.write('   - name: jobiation_commands\n');
playbookfile.write('     ios_command:\n');
playbookfile.write('      commands:\n');
for cmd in commandsfile:
    playbookfile.write('       - ' + cmd);
with inventoryfile as csvfile:
    datareader = csv.reader(csvfile)
    for row in datareader:
        devicename = row[0];
        active = row[1];
        ip = row[2];
        arg3 = row[7];
# Note that continue means skip.
# Conditions must be casted as strings

        if str(arg3) != '1':
            continue;

        if str(active) != '1':
            continue;

        if str(devicename) == 'devicename':
            continue;

        if str(devicename) == 'skipline':
            continue;
        hostsfile.write('       ' + devicename + ':\n');
        hostsfile.write('         ansible_host: ' + ip + '\n');

inventoryfile.close();
hostsfile.close();
playbookfile.close();
commandsfile.close();