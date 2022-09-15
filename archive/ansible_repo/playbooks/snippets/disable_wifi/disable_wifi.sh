#!/bin/bash

    /usr/bin/ansible-playbook --vault-id ansiblevaultuser@/var/.ansiblecreds "/etc/ansible/playbooks/disable_wifi/disable_wifi.yml"
