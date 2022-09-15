#!/bin/bash

mv /var/ansiblerepo/hosts /etc/ansible/hosts


/usr/bin/ansible-playbook --vault-id ansiblevaultuser@/var/cons/.ansiblecreds "/var/ansiblerepo/playbooks/ansible_upgrade_ios/ansible_temp_task.yaml" > /var/ansiblerepo/playbooks/ansible_upgrade_ios/output/playbooks_results.txt

rm /etc/ansible/hosts
