#!/usr/bin/env python3
import csv
import os
aclgroup = 'tACL';
hostsfile = open('jobs/20221230_2107/hosts', 'a+');
inventoryfile = open('../inventory.csv', 'r');
playbookfile = open('jobs/20221230_2107/jobiation_task.yaml', 'w');
playbookfile.write('---\n');
with inventoryfile as invfile:
    invdata = csv.reader(invfile)
    for row in invdata:
        devicename = row[0];
        active = row[1];
        ip = row[2];
        arg3 = row[7];
        tACL_dir = row[11];
        locallan1 = row[12];
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
        if os.path.isfile('tmp/'+aclgroup+'/'+devicename+'.txt'):
            commandsfile = open('tmp/'+aclgroup+'/'+devicename+'.txt', 'r');
        else:
            commandsfile = open('tmp/tACL/standard_template.txt', 'r');
        for cmd in commandsfile:
            repstr = cmd;
            repstr = repstr.replace('!tACL_dir!', tACL_dir);
            repstr = repstr.replace('!locallan1!', locallan1);
            playbookfile.write('       - ' + repstr);
        commandsfile.close();
        playbookfile.write('\n###############################################################\n');

inventoryfile.close();
hostsfile.close();
playbookfile.close();
