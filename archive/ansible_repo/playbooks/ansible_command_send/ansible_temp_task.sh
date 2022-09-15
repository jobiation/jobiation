#!/bin/bash


mv /var/ansiblerepo/hosts /etc/ansible/hosts


/usr/bin/ansible-playbook --vault-id ansiblevaultuser@/var/cons/.ansiblecreds "/var/ansiblerepo/playbooks/ansible_command_send/ansible_temp_task.yaml" > /var/ansiblerepo/playbooks/ansible_command_send/output/playbooks_results.txt

rm /etc/ansible/hosts

