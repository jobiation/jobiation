#!/bin/bash
/usr/bin/ansible-playbook --vault-id ansiblevaultuser@/var/cons/.ansiblecreds jobs/20221009_1945/ansible_task.yaml > jobs/20221009_1945/playbook_result.txt