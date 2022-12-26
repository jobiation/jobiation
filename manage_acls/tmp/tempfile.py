#!/usr/bin/env python3
import csv
import sys
import shutil
import os
hostsfile = open('jobs/20221226_1522/hosts', 'a+');
inventoryfile = open('../inventory.csv', 'r');
commandsfile = open('templates/TACL.txt', 'r');
playbookfile = open('jobs/20221226_1522/jobiation_task.yaml', 'w');
playbookfile.write('---\n');
with inventoryfile as invfile:
    invdata = csv.reader(invfile)
    for row in invdata:
        devicename = row[0];
        active = row[1];
        ip = row[2];
        arg3 = row[7];
        locallan1 = row[13];
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
        hostsfile.write('       ' + devicename + ':\n');
        hostsfile.write('         ansible_host: ' + ip + '\n');
        playbookfile.write('- name: ' + devicename + '_pb\n');
        playbookfile.write('  hosts: ' + devicename + '\n');
        playbookfile.write('  gather_facts: no\n');
        playbookfile.write('  vars:\n');
        playbookfile.write('   ansible_command_timeout: 30\n');
        playbookfile.write('  tasks:\n');
        playbookfile.write('   - name: ' + devicename + '_commands\n');
        playbookfile.write('     cisco.ios.ios_command:\n');
        playbookfile.write('      commands:\n');
        playbookfile.write('       - interface g0/0/0\n');
        playbookfile.write('       - no ip access-group TunnelACL in\n');
        playbookfile.write('       - interface TunnelACL 100\n');
        playbookfile.write('       - no ip access-group TunnelACL in\n');
        playbookfile.write('       - no ip access-list extended TunnelACL\n');
        commandsfile = open('templates/TACL.txt', 'r');
        for cmd in commandsfile:
            repstr = cmd;
            repstr = repstr.replace('!locallan1', locallan1);
            playbookfile.write('       - ' + repstr);
        playbookfile.write('       - ip access-list extended TunnelACL\n');
        playbookfile.write('       - interface g0/0/0\n');
        playbookfile.write('       - ip access-group TunnelACL in\n');
        playbookfile.write('       - interface TunnelACL 100\n');
        playbookfile.write('       - ip access-group TunnelACL in\n');
        playbookfile.write('\n###############################################################\n');

inventoryfile.close();
hostsfile.close();
playbookfile.close();
commandsfile.close();