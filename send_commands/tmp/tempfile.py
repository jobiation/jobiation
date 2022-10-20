#!/usr/bin/env python3
import csv
import sys
import shutil
import os
hostsfile = open('jobs/20221019_2116/hosts', 'a+');
inventoryfile = open('../inventory.csv', 'r');
commandsfile = open('commands.txt', 'r');
playbookfile = open('jobs/20221019_2116/jobiation_task.yaml', 'w');
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
playbookfile.write('       command: "reload in 1"\n');
playbookfile.write('       check_all: True\n');
playbookfile.write('       prompt:\n');
playbookfile.write('         - "Confirm"\n');
playbookfile.write('       answer:\n');
playbookfile.write('         - "y"\n');
playbookfile.write('   - name: gather_facts\n');
playbookfile.write('     cisco.ios.ios_facts:\n');
playbookfile.write('     register: jobiation_facts\n');
playbookfile.write('   - name: run_show_command\n');
playbookfile.write('     cisco.ios.ios_command:\n');
playbookfile.write('       commands: show running-config\n');
playbookfile.write('     register: jobiation_showcmd\n');
playbookfile.write('   - name: jobiation_commands\n');
playbookfile.write('     cisco.ios.ios_command:\n');
playbookfile.write('      commands:\n');
for cmd in commandsfile:
    playbookfile.write('       - ' + cmd);
playbookfile.write('\n');
playbookfile.write('     when: jobiation_facts["ansible_facts"]["ansible_net_interfaces"]["GigabitEthernet0/0/0"]["macaddress"] == "2436.daf2.dc00" and jobiation_showcmd is search("ip name-server 192.168.254.254")\n');
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
hostsfile.write('       ' + devicename + ':\n');
hostsfile.write('         ansible_host: ' + ip + '\n');

inventoryfile.close();
hostsfile.close();
playbookfile.close();
commandsfile.close();