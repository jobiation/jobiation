#!/usr/bin/env python3

import csv
import sys
import shutil
import os

hostsfile = open("tmp/hosts", "a+");
# playbookfile = open("/var/ansiblerepo/playbooks/ansible_get_output_py/ansible_task.yaml", "w+");
# playbookfile.write("---\n");
inventoryfile = open("../inventory.csv", "r");
with inventoryfile as csvfile:
    datareader = csv.reader(csvfile)
    for row in datareader:
