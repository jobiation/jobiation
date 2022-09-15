#!/bin/bash

ansible-vault encrypt_string --vault-id ansiblevaultuser@prompt 'mytacacspassword' --name 'ansible_password'

