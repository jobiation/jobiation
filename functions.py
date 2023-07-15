#!/usr/bin/emv python3

#    Copyright 2023 Anthony Tranquillo

#    This file is part of Jobiation.

#    Jobiation is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

#    Jobiation is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License along with Jobiation.  If not, see <http://www.gnu.org/licenses/>.

import sys;
import shutil;
import re;
import os;
import subprocess;
import re;
import csv;

import validations;

def reloadIn(tempfile,reload_in, spaces):
    tempfile.write(spaces+"playbookfile.write('   - name: Write\\n');\n");
    tempfile.write(spaces+"playbookfile.write('     cli_command:\\n');\n");
    tempfile.write(spaces+"playbookfile.write('       command: \"write\"\\n');\n");
    tempfile.write(spaces+"playbookfile.write('   - name: Reload\\n');\n");
    tempfile.write(spaces+"playbookfile.write('     cli_command:\\n');\n");
    tempfile.write(spaces+"playbookfile.write('       command: \"reload in " + str(reload_in) + "\"\\n');\n");
    tempfile.write(spaces+"playbookfile.write('       check_all: True\\n');\n");
    tempfile.write(spaces+"playbookfile.write('       prompt:\\n');\n");
    tempfile.write(spaces+"playbookfile.write('         - \"Confirm\"\\n');\n");
    tempfile.write(spaces+"playbookfile.write('       answer:\\n');\n");
    tempfile.write(spaces+"playbookfile.write('         - \"y\"\\n');\n");

def copyFile(tempfile,copy_file_cmd,image_file_name,filename_prompt):
    tempfile.write("playbookfile.write('   - name: copy_file\\n');\n");
    tempfile.write("playbookfile.write('     cli_command:\\n');\n");
    tempfile.write("playbookfile.write('       command: \"" + copy_file_cmd + "\"\\n');\n");
    tempfile.write("playbookfile.write('       check_all: True\\n');\n");
    tempfile.write("playbookfile.write('       prompt:\\n');\n");
    tempfile.write("playbookfile.write('         - \"" + filename_prompt + "\"\\n');\n");
    tempfile.write("playbookfile.write('       answer:\\n');\n");
    tempfile.write("playbookfile.write('         - \"" + image_file_name + "\"\\n');\n");

def promptReload(current_dir,reload_in,scheduled_task):
    confirm_reload = "yes";
    if reload_in <= 0 or not re.search(validations.numericreg,str(reload_in)):
        print("\nThe reload_in value must be a positive integer between 1 and 9999.\n");
        shutil.rmtree(current_dir);
        sys.exit();
    if scheduled_task == "NA":
        confirm_reload = input("\n-- ATTENTION! You have the reload_in option enabled.\n\n-- Your specified devices will be reloaded in " + str(reload_in) + " minutes.\n\n-- Type 'yes' if you want to continue or type 'quit'. ");
    if confirm_reload.lower() != "yes":
        print("\nAborting!\n");
        shutil.rmtree(current_dir);
        sys.exit();
    
def abortPlaybook(current_dir,message,rmdir):
    print(message);
    if rmdir:
        shutil.rmtree(current_dir);
        print("Removing job directory.");
    sys.exit();

def getFirstLine(inventoryfile):
    with inventoryfile as invrow:
        firstline = invrow.readline();
    inventoryfile.close();
    return firstline.split(",");

def removeBecome(current_dir):
    with open(current_dir + "/hosts.yaml", "r") as hosts:
        hostslines = hosts.readlines();
    hosts.close();
    remove_until_ansible_username = 0;
    with open(current_dir + "/hosts.yaml", "w") as hosts:
        for hostsline in hostslines:
            matchbecome = re.search('ansible_become_password:', hostsline);
            matchuser = re.search('ansible_user:', hostsline);
            if remove_until_ansible_username == 0 or matchuser:
                if matchuser:
                    remove_until_ansible_username = 0;
                if matchbecome:
                    print("\nRemoving become password from hosts file.\n");
                    remove_until_ansible_username = 1;
                else:
                    hosts.write(hostsline);
    hosts.close();

def removeUser(current_dir):
    with open(current_dir + "/hosts.yaml", "r") as hosts:
        hostslines = hosts.readlines();
    hosts.close();
    remove_until_ansible_password = 0;
    with open(current_dir + "/hosts.yaml", "w") as hosts:
        for hostsline in hostslines:
            matchuser = re.search('ansible_user:', hostsline);
            matchpass = re.search('ansible_password:', hostsline);
            if remove_until_ansible_password == 0 or matchpass:
                if matchpass:
                    remove_until_ansible_password = 0;
                if matchuser:
                    print("\nRemoving username from hosts file.\n");
                    remove_until_ansible_password = 1;
                else:
                    hosts.write(hostsline);
    hosts.close();

def removePass(current_dir):
    with open(current_dir + "/hosts.yaml", "r") as hosts:
        hostslines = hosts.readlines();
    hosts.close();
    remove_until_children = 0;
    with open(current_dir + "/hosts.yaml", "w") as hosts:
        for hostsline in hostslines:
            matchchildren = re.search('children:', hostsline);
            matchpass = re.search('ansible_password:', hostsline);
            if remove_until_children == 0 or matchchildren:
                if matchchildren:
                    remove_until_children = 0;
                if matchpass:
                    print("\nRemoving Password from hosts file.\n");
                    remove_until_children = 1;
                else:
                    hosts.write(hostsline);
    hosts.close();

def removeHostsHeader(hosts_header):
    if os.path.exists(hosts_header):
        os.remove(hosts_header);

def confirmReady(current_dir,scheduled_task):
    confirm_ready = "";
    if scheduled_task == "NA":
        confirm_ready = input("\n\n-- Your playbook and hosts file is ready.\n\n-- Please open them in " + current_dir + ".\n\n-- Make sure the commands are the commands you intend to perform on your Cisco devices.\n\n-- Press ENTER when ready or type quit.\n\n");
    if(confirm_ready != ""):
        print("\nAborting!\n");
        shutil.rmtree(current_dir);
        sys.exit();

def runPlaybook(current_dir,playbook_path,password_prompt,running_msg,finished_msg,results_file,ansible_exe):
    bashfile = open("tmp/runplaybook.sh","w");
    bashfile.write('#!/bin/bash\n');
    bashfile.write(ansible_exe + " " + playbook_path + " -i " + current_dir + "/hosts.yaml" + password_prompt + " > " + current_dir + "/" + results_file);
    bashfile.close();
    print(running_msg);
    os.chmod("tmp/runplaybook.sh", 0o770);
    subprocess.call("tmp/runplaybook.sh");
    print(finished_msg);

def makeCurrentDir(date_time,prepend_job_name):
    if os.path.isdir('jobs/' + prepend_job_name + date_time):
        print("\nYou cannot run more than one job within the same minute. Please wait until the end of this minute and try again.\n");
        sys.exit();
    else:
        os.mkdir('jobs/' + prepend_job_name + date_time);
        return "jobs/" + prepend_job_name + date_time;

def makeHostsHeader(current_dir,ansible_python_interpreter,ansible_connection,ansible_network_os,ansible_port,username,become_necessary):
    hostsfile = open(current_dir+"/hosts.yaml","w");
    hostsfile.write("---\n");
    hostsfile.write("all:\n");   
    hostsfile.write(" vars:\n");
    hostsfile.write("  ansible_python_interpreter: " + ansible_python_interpreter + "\n");
    hostsfile.write("  ansible_connection: " + ansible_connection + "\n");
    hostsfile.write("  ansible_network_os: " + ansible_network_os + "\n");
    hostsfile.write("  ansible_port: " + str(ansible_port) + "\n");
    hostsfile.write("  ansible_become: " + become_necessary + "\n");
    hostsfile.write("  ansible_become_method: enable\n");
    hostsfile.write("  ansible_user: " + username + "\n");
    hostsfile.write(" children:\n");
    hostsfile.write("   jobiation_inventory:\n");
    hostsfile.write("     hosts:\n");
    hostsfile.close();

def checkReqDir():
    if not os.path.isdir('jobs'):
        os.mkdir('jobs');
    if not os.path.isdir('tmp'):
        os.mkdir('tmp');

def convertLineEnd(current_dir,yfile):
    tempfile = open("tmp/tempfile.py","w");
    yamlfile = open(current_dir+"/"+yfile,"r");
    for yline in yamlfile:
        tempfile.write(yline.strip("\n")+"\r\n");
    tempfile.close();
    yamlfile.close();
    shutil.copyfile("tmp/tempfile.py", current_dir + "/" + yfile);

def validateDevicename(inventory_file,devicenameAllowed,current_dir,message,index):
    with inventory_file as invfile:
        invdata = csv.reader(invfile);
        for row in invdata:
            if not re.search(devicenameAllowed, row[int(index)]):
                print("\n!"+row[int(index)]+message);
                shutil.rmtree(current_dir);
                sys.exit();

def getListIndex(list,listElement):
    for l in list:
        if l == listElement:
            return str(list.index(l));

def validateArg(argNameAllowed,argName,badArgNameMsg):
    if not re.search(argNameAllowed, argName):
        if not argName == "NA":
            print("\n!"+argName+badArgNameMsg);
            sys.exit();

def validateReqCol(req_columns,flList):
    for col in req_columns:
        if not col in flList:
            print("Your inventory needs a column called '" + col + "'");
            sys.exit();

def validateFirstLine(flList,current_dir,badFirstLine):
    for flCol in range(len(flList)-1):
        if not re.search(validations.flAllowedChars, str(flList[flCol])):
            print("\n!"+flList[flCol] + badFirstLine);
            shutil.rmtree(current_dir);
            sys.exit();

def setRevertTimer(tempfile,spaces,cisco_command_type,revert_timer,archive_path):
    tempfile.write(spaces + "playbookfile.write('   - name: config_revert\\n');\n");
    tempfile.write(spaces + "playbookfile.write('     " + cisco_command_type + ":\\n');\n");
    tempfile.write(spaces + "playbookfile.write('      commands:\\n');\n");
    if not archive_path == "":
        tempfile.write(spaces + "playbookfile.write('       - configure terminal\\n');\n");
        tempfile.write(spaces + "playbookfile.write('       - archive\\n');\n");
        tempfile.write(spaces + "playbookfile.write('       - \\'" + archive_path + "\\'\\n');\n");
        tempfile.write(spaces + "playbookfile.write('       - end\\n');\n");
    tempfile.write(spaces + "playbookfile.write('       - configure terminal revert timer " + str(revert_timer) + "\\n');\n");
    tempfile.write(spaces + "playbookfile.write('       - end\\n');\n");

def confirmConfig(tempfile,spaces,cisco_command_type):
    tempfile.write(spaces + "playbookfile.write('   - name: config_confirm\\n');\n");
    tempfile.write(spaces + "playbookfile.write('     " + cisco_command_type + ":\\n');\n");
    tempfile.write(spaces + "playbookfile.write('      commands:\\n');\n");
    tempfile.write(spaces + "playbookfile.write('       - configure confirm\\n');\n");
    tempfile.write(spaces + "playbookfile.write('       - write\\n');\n");

def notifyFailure(notify_script,notify_recipients,notify_subject,current_dir,calling_script):
    message = calling_script + "/" + current_dir + "\r\n\r\n\r\n";
    notify = 0;
    results_file = open(current_dir+"/playbook_results.txt","r");
    for line in results_file:
        if "failed=1" in line or "unreachable=1" in line or "skipped=1" in line or "rescured=1" in line or "ignored=1" in line:
            message = message + "--- " + line + "\r\n\r\n";
            notify = 1;
    results_file.close();
    if notify == 1:
        subprocess.call(notify_script+" '"+message+"' '"+notify_recipients+"' '"+notify_subject+"'",shell=True);
 