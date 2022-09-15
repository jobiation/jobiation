#!/bin/bash

mv /var/ansiblerepo/hosts /etc/ansible

/usr/bin/ansible-playbook --vault-id ansiblevaultuser@/var/.ansiblecreds "/var/ansiblerepo/playbooks/device_backup/device_backup.yaml"

rm /etc/ansible/hosts
