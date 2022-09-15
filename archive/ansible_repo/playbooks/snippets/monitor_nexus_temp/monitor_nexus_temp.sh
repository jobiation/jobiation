#!/bin/bash

/usr/bin/ansible-playbook --vault-id ansiblevaultuser@/var/temoraclo3/.ansiblecreds "/etc/ansible/playbooks/monitor_nexus_temp/monitor_nexus_temp.yml"


