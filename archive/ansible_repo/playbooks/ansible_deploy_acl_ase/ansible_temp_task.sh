#!/bin/bash


mv /var/ansiblerepo/hosts /etc/ansible/hosts


/usr/bin/ansible-playbook "/var/ansiblerepo/playbooks/ansible_deploy_acl_ase/ansible_temp_task.yaml" -k > /var/ansiblerepo/playbooks/ansible_deploy_acl_ase/output/playbooks_results.txt

rm /etc/ansible/hosts

