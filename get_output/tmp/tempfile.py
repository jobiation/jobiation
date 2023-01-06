#!/usr/bin/env python3
import csv
import sys
import shutil
import os
hostsfile = open('jobs/20230105_2040/hosts', 'a+');
inventoryfile = open('../inventory.csv', 'r');
playbookfile = open('jobs/20230105_2040/jobiation_task.yaml', 'w');
playbookfile.write('---\n');
playbookfile.write('- name: jobiation_pb\n');
playbookfile.write('  hosts: jobiation_inventory\n');
playbookfile.write('  gather_facts: no\n');
playbookfile.write('  vars:\n');
playbookfile.write('   ansible_command_timeout: 30\n');
playbookfile.write('  tasks:\n');
playbookfile.write('   - name: gather_facts\n');
playbookfile.write('     cisco.ios.ios_facts:\n');
playbookfile.write('     register: jobiation_facts\n');
playbookfile.write('   - name: copy_output_to_file\n');
playbookfile.write('     copy: content="{{ jobiation_facts }}" dest="jobs/20230105_2040/facts/{{ inventory_hostname }}_facts.txt"\n');
playbookfile.write('   - name: showrun\n');
playbookfile.write('     cisco.ios.ios_command:\n');
playbookfile.write('       commands: show running-config\n');
playbookfile.write('     register: showrun\n');
playbookfile.write('   - name: copy_output_to_file\n');
playbookfile.write('     copy: content="{{ showrun.stdout[0] }}" dest="jobs/20230105_2040/showrun/{{ inventory_hostname }}_showrun.txt"\n');
playbookfile.write('   - name: showver\n');
playbookfile.write('     cisco.ios.ios_command:\n');
playbookfile.write('       commands: show version\n');
playbookfile.write('     register: showver\n');
playbookfile.write('   - name: copy_output_to_file\n');
playbookfile.write('     copy: content="{{ showver.stdout[0] }}" dest="jobs/20230105_2040/showver/{{ inventory_hostname }}_showver.txt"\n');
with inventoryfile as invfile:
    invdata = csv.reader(invfile)
    for row in invdata:
        devicename = row[0];
        active = row[1];
        ip = row[2];
        arg3 = row[5];
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
