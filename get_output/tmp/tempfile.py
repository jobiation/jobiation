#!/usr/bin/env python3
import csv
import sys
import shutil
import os
hostsfile = open('jobs/20230107_1101/hosts', 'a+');
inventoryfile = open('../inventory.csv', 'r');
playbookfile = open('jobs/20230107_1101/jobiation_task.yaml', 'w');
playbookfile.write('---\n');
playbookfile.write('- name: jobiation_pb\n');
playbookfile.write('  hosts: jobiation_inventory\n');
playbookfile.write('  gather_facts: no\n');
playbookfile.write('  vars:\n');
playbookfile.write('   ansible_command_timeout: 30\n');
playbookfile.write('  tasks:\n');
playbookfile.write('   - name: sh8W_run_\n');
playbookfile.write('     cisco.ios.ios_command:\n');
playbookfile.write('       commands: show running-config\n');
playbookfile.write('     register: sh8W_run_\n');
playbookfile.write('   - name: copy_output_to_file\n');
playbookfile.write('     copy: content="{{ sh8W_run_.stdout[0] }}" dest="jobs/20230107_1101/sh8W_run_/{{ inventory_hostname }}_sh8W_run_.txt"\n');
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
