#!/usr/bin/env python3
import csv
import sys
import shutil
import os
hostsfile = open('jobs/20221011_2038/hosts', 'a+');
inventoryfile = open('../inventory.csv', 'r');
commandsfile = open('commands.txt', 'r');
playbookfile = open('jobs/20221011_2038/jobiation_task.yaml', 'w');
playbookfile.write('---\n');
with inventoryfile as csvfile:
    datareader = csv.reader(csvfile)
    for row in datareader:
        devicename = row[0];
        active = row[1];
        ip = row[2];
        arg2 = row[6];
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
        hostsfile.write('       ' + devicename + ':\n');
        hostsfile.write('         ansible_host: ' + ip + '\n');
        playbookfile.write('- name: ' + devicename + '_pb\n');
        playbookfile.write('  hosts: ' + devicename + '\n');
        playbookfile.write('  gather_facts: no\n');
        playbookfile.write('  vars:\n');
        playbookfile.write('   ansible_command_timeout: 30\n');
        playbookfile.write('  tasks:\n');
        playbookfile.write('   - name: Gather all legacy facts\n');
        playbookfile.write('     cisco.ios.ios_facts:\n');
        playbookfile.write('       gather_subset: all\n');
        playbookfile.write('     register: ios_facts\n');
        playbookfile.write('   - name: ' + devicename + '_commands\n');
        playbookfile.write('     ios_command:\n');
        playbookfile.write('      commands:\n');
        commandsfile = open('commands.txt', 'r');
        for cmd in commandsfile:
            repstr = cmd;
            repstr = repstr.replace('!arg2', arg2);
            playbookfile.write('       - ' + repstr);
        playbookfile.write('     when: ios_facts["ansible_facts"]["ansible_net_interfaces"]["GigabitEthernet0/0/0"]["macaddress"] == "2436.daf2.dc00"\n');
        playbookfile.write('\n###############################################################\n');

inventoryfile.close();
hostsfile.close();
playbookfile.close();
commandsfile.close();