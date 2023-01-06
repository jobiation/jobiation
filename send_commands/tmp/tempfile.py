#!/usr/bin/env python3
import csv
hostsfile = open('jobs/20230105_2037/hosts', 'a+');
inventoryfile = open('../inventory.csv', 'r');
commandsfile = open('commands.txt', 'r');
playbookfile = open('jobs/20230105_2037/jobiation_task.yaml', 'w');
playbookfile.write('---\n');
with inventoryfile as invfile:
    invdata = csv.reader(invfile)
    for row in invdata:
        devicename = row[0];
        active = row[1];
        ip = row[2];
        arg1 = row[3];
        arg3 = row[5];
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
        commandsfile = open('commands.txt', 'r');
        for cmd in commandsfile:
            repstr = cmd;
            repstr = repstr.replace('!arg1!', arg1);
            repstr = repstr.replace('!datalan!', datalan);
            playbookfile.write('       - ' + repstr);
        playbookfile.write('\n');
        playbookfile.write('\n###############################################################\n');

inventoryfile.close();
hostsfile.close();
playbookfile.close();
commandsfile.close();