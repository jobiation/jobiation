#!/usr/bin/env python3

#    Copyright 2023 Anthony Tranquillo

#    This file is part of Jobiation.

#    Jobiation is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

#    Jobiation is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License along with Jobiation.  If not, see <http://www.gnu.org/licenses/>.

import subprocess;
import sys;
import os;
from pwd import getpwnam;
import getpass;

# Get the logged in user's uid and gid
current_user = os.getlogin();
user_uid = getpwnam(current_user).pw_uid;
user_gid = getpwnam(current_user).pw_gid;

print("\n\n........................Ansible Install...................\n");
print("Would you like to install and configure Ansible on this server?\n");
installansible = input("Press y to proceed with installing Ansible [y/n] ");

if installansible.lower() == "y":
    # Install Ansible
    subprocess.call("./ansible_install.sh",shell=True);

    # Create the /etc/ansible and set permissions
    if not os.path.isdir("/etc/ansible"):
        os.mkdir("/etc/ansible");

    os.chmod("/etc/ansible", 0o755);
    os.chown("/etc/ansible",user_uid,user_gid);

    # Create /etc/ansible/ansible.cfg and set host_key_checking
    ansible_config_file = open("/etc/ansible/ansible.cfg","a+");
    ansible_config_file.write("[defaults]\n");
    ansible_config_file.write("host_key_checking = False\n");
    ansible_config_file.close();

    # Set permissions
    os.chmod("/etc/ansible/ansible.cfg", 0o644);
    os.chown("/etc/ansible/ansible.cfg",user_uid,user_gid);

# Ask user if they want to install Samba
print("\n\n........................Samba Install...................\n");
print("Would you like to install Samba on this server?\n");
print("If "+current_user+"'s home directory is not in /home, the Samba install will fail.\n");
print("If you proceed with installing Samba you will be promted to set a Samba password for "+current_user+".\n");
installsmb = input("Press y to proceed with installing Samba [y/n] ");

if installsmb.lower() == "y":

    # Install Samba
    subprocess.call("./samba_install.sh");

    # Prompt the user to set a Samba password.
    subprocess.call("./samba_set_user.sh '"+current_user+"'",shell=True);

    # Add the jobiation share to smb.conf
    sambafile = open("/etc/samba/smb.conf","+a");
    sambafile.write("[jobiation]\n");
    sambafile.write("  comment = jobiation directory\n");
    sambafile.write("  browseable = yes\n");
    sambafile.write("  path = /home/"+current_user+"/jobiation\n");
    sambafile.write("  guest ok = no\n");
    sambafile.write("  read only = no\n");
    sambafile.write("  create mask = 0600\n");
    sambafile.write("  directory mask = 0700\n");
    sambafile.write("  valid users = "+current_user+"\n");
    sambafile.close();

    # Restart Samba
    subprocess.call("./samba_restart.sh");

# Ask user if they want to install MUTT
print("\n\n........................MUTT Install...................\n");
print("Would you like to receive email notificatons from this server?\n");
print("If so, MUTT will be installed and setup to use a Gmail address as an example.\n");
print("If you would like to use a service other than Gmail you can tweak the settings after the script is finished.\n");
installmutt = input("Press y to proceed with installing MUTT? [y/n] ");

if installmutt.lower() == "y":
    sender_email = input("\nType the portion of the gmail address before the @. In other words, do not write the @gmail.com part. ");
    sender_app_pass = getpass.getpass("What is the app specific password? ");
    subprocess.call("./mutt_install.sh",shell=True);
    if not os.path.isdir("/home/"+current_user+"/.mutt"):
        os.mkdir("/home/"+current_user+"/.mutt");
    muttfile = open("/home/"+current_user+"/.mutt/muttrc","w");
    muttfile.write("set ssl_force_tls = yes\n");
    muttfile.write("set realname = 'Jobiation Notifications'\n");
    muttfile.write("set from = '"+sender_email+"@gmail.com'\n");
    muttfile.write("set smtp_url = 'smtps://"+sender_email+"@smtp.gmail.com'\n");
    muttfile.write("set smtp_pass = '"+sender_app_pass+"'\n");
    muttfile.close();

    os.chmod("/home/"+current_user+"/.mutt", 0o700);
    os.chmod("/home/"+current_user+"/.mutt/muttrc", 0o600);
    os.chown("/home/"+current_user+"/.mutt",user_uid,user_gid);
    os.chown("/home/"+current_user+"/.mutt/muttrc",user_uid,user_gid);

# Ask user if they want to install Ansible Vault
print("Would you like to configure Ansible Vault now?\n");
installvault = input("Press y to proceed with configuring Ansible Vault? [y/n] ");

if installvault.lower() == "y":
    
    # Create secret file
    secret_file_loc = "/home/"+current_user+"/.vault_pass";

    # Open hosts_header files
    hosts_header_sample = open("hosts_header_template","r");
    hosts_header_file = open("hosts_header","w");

    # Prompt the user for input.
    device_username = input("Device username: ");
    device_password = getpass.getpass("Device Password: ");
    device_become = getpass.getpass("Enable password: ");
    vault_username = input("Ansible Vault username: ");
    vault_password = getpass.getpass("Ansible Vault password: ");

    # Write the vault password to the vault file
    secret_file = open(secret_file_loc,"w");
    secret_file.write(vault_password);
    secret_file.close();
    os.chmod(secret_file_loc, 0o600);
    os.chown(secret_file_loc,user_uid,user_gid);

    # Create encrypted username, password, and become file
    bashfile = open("runvaultcmd.sh","w");
    bashfile.write('#!/bin/bash\n');
    bashfile.write("echo 'Enter your Ansible Vault password twice to encrypt your ansible_password';\n");
    bashfile.write("ansible-vault encrypt_string --encrypt-vault-id " + vault_username + " --vault-id " + vault_username + "@prompt '" + device_password + "' --name 'ansible_password' > encpassword.txt\n");
    bashfile.write("echo 'Enter your Ansible Vault password twice to encrypt your ansible_username';\n");
    bashfile.write("ansible-vault encrypt_string --encrypt-vault-id " + vault_username + " --vault-id " + vault_username + "@prompt '" + device_username + "' --name 'ansible_user' > encusername.txt\n");
    bashfile.write("echo 'Enter your Ansible Vault password twice to encrypt your ansible_become_password (AKA enable password)';\n");
    bashfile.write("ansible-vault encrypt_string --encrypt-vault-id " + vault_username + " --vault-id " + vault_username + "@prompt '" + device_become + "' --name 'ansible_become_password' > encbecome.txt");
    bashfile.close();
    os.chmod("runvaultcmd.sh", 0o770);
    subprocess.call("./runvaultcmd.sh");

    # Open temp files for encrypted strings
    encpassword_file = open("encpassword.txt","r");
    encusername_file = open("encusername.txt","r");
    encbecome_file = open("encbecome.txt","r");

    # Build hosts_header file
    for hhsline in hosts_header_sample:
        if("ansible_become_password:" in hhsline):
            for abpline in encbecome_file:
                hosts_header_file.write("  "+abpline);
        elif("ansible_user:" in hhsline):
            for auline in encusername_file:
                hosts_header_file.write("  "+auline);
        elif("ansible_password:" in hhsline):
            for apline in encpassword_file:
                hosts_header_file.write("  "+apline);
        else:
            hosts_header_file.write(hhsline);

    # Close files
    encpassword_file.close();
    encusername_file.close();
    encbecome_file.close();
    hosts_header_file.close();
    hosts_header_sample.close();

    # In /etc/ansible/ansible.cfg, set vault_password_file
    ansible_config_file = open("/etc/ansible/ansible.cfg","+a");
    ansible_config_file.write("vault_password_file = /home/"+current_user+"/.vault_pass\n");
    ansible_config_file.close();

    # Empty variables
    device_username = "";
    device_password = "";
    device_become = "";
    vault_username = "";
    vault_password = "";

    # Cleanup files
    os.remove("encusername.txt");
    os.remove("encpassword.txt");
    os.remove("encbecome.txt");
    os.remove("runvaultcmd.sh");

    # Change ownership of hosts_header file
    os.chown("hosts_header",user_uid,user_gid);