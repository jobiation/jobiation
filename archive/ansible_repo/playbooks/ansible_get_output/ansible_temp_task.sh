#!/bin/bash

mv /var/ansiblerepo/hosts /etc/ansible/hosts


# /usr/bin/ansible-playbook --vault-id ansiblevaultuser@prompt "/var/ansiblerepo/playbooks/ansible_get_output/ansible_temp_task.yaml" --ask-vault-pass > /var/ansiblerepo/playbooks/ansible_get_output/output/playbook_result.txt

/usr/bin/ansible-playbook --vault-id ansiblevaultuser@/var/cons/.ansiblecreds "/var/ansiblerepo/playbooks/ansible_get_output/ansible_temp_task.yaml" > /var/ansiblerepo/playbooks/ansible_get_output/output/playbook_results.txt

rm /etc/ansible/hosts

