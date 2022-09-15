#!/usr/bin/env python3

import csv
import sys
import shutil
import os

hostsfile = open("/var/ansiblerepo/playbooks/ansible_get_output_py/hosts", "a+");
# playbookfile = open("/var/ansiblerepo/playbooks/ansible_get_output_py/ansible_task.yaml", "w+");
# playbookfile.write("---\n");
devicesfile = open("/var/ansiblerepo/playbooks/ansible_get_output_py/ansibledevices.csv", "r");
with devicesfile as csvfile:
    datareader = csv.reader(csvfile)
    for row in datareader:
