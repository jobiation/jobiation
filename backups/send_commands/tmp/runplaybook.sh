#!/bin/bash
/usr/bin/ansible-playbook jobs/20221001_1415/jobiation_task.yaml -i jobs/20221001_1415/hosts -k > jobs/20221001_1415/playbook_result.txt