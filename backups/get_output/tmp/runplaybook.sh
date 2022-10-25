#!/bin/bash
/usr/bin/ansible-playbook --vault-id ansiblevaultuser@/var/.ansiblecreds jobs/20220825_1605/ansible_task.yaml -u -k > jobs/20220825_1605/playbook_result.txt