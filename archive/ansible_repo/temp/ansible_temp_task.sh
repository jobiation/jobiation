#!/bin/bash


ansible -m  setup -i /etc/ansible/hosts myrouter

# /usr/bin/ansible-playbook --vault-id ansiblevaultuser@prompt "/var/ansiblerepo/playbooks/ansible_get_output/ansible_temp_task.yaml" --ask-vault-pass > /var/ansiblerepo/playbooks/ansible_get_output/output/playbook_result.txt

#/usr/bin/ansible-playbook --vault-id ansiblevaultuser@/var/cons/.ansiblecreds "/var/ansiblerepo/temp/ansible_temp_task.yaml"

#rm /etc/ansible/hosts

