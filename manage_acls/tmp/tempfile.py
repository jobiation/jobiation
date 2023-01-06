#!/usr/bin/env python3
import csv
import os
aclgroup = 'tunnelACL';
hostsfile = open('jobs/20230105_2055/hosts', 'a+');
inventoryfile = open('../inventory.csv', 'r');
playbookfile = open('jobs/20230105_2055/jobiation_task.yaml', 'w');
playbookfile.write('---\n');
with inventoryfile as invfile:
    invdata = csv.reader(invfile)
    for row in invdata:
        devicename = row[0];
        active = row[1];
        ip = row[2];
        arg3 = row[5];
        TunnelACL_dir = row[7];
        datalan = row[8];
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
            commandsfile = open('tmp/tunnelACL/standard_template.txt', 'r');
        for cmd in commandsfile:
            repstr = cmd;
            repstr = repstr.replace('!TunnelACL_dir!', TunnelACL_dir);
            repstr = repstr.replace('!datalan!', datalan);
            playbookfile.write('       - ' + repstr);
        commandsfile.close();
        playbookfile.write('\n###############################################################\n');

inventoryfile.close();
hostsfile.close();
playbookfile.close();
