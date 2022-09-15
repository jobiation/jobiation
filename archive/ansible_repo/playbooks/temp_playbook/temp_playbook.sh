#!/bin/bash

/usr/bin/ansible-playbook --vault-id ansiblevaultuser@/var/.ansiblecreds "/etc/ansible/playbooks/temp_playbook/temp_playbook.yml"

