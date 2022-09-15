# # Enable service account

# Set variables
    $ansible_server = "ansible";
    $devices_location = "..\devices.csv";
    $host_cond_loc = "..\host_conditions.ps1"; # Hosts conditions location
    $textedit_loc = "C:\Users\me\AppData\Local\Programs\Microsoft VS Code\Code.exe";

# Import devices.csv and commands.txg
    $devices = Import-CSV $devices_location;

# Create a directory for the files
    $current_time=get-date -uformat %Y%m%d_%H%M%S
    $current_dir = ".\playbooks\$current_time";
    mkdir $current_dir;

    $timeout_seconds = read-host "How many seconds command timeout? (Press ENTER for default 30 seconds)";
    if("$timeout_seconds" -eq ""){$timeout_seconds = "30";}

    $reload_minutes = read-host "How many minutes until reload? (Press ENTER for default 720 minutes)";
    if("$reload_minutes" -eq ""){$reload_minutes = "720";}

    $config_register = read-host "Set the config register? (Press ENTER to make make it 0x2102)";
    if("$config_register" -eq ""){$config_register = "0x2102";}

    $copy_command = read-host "Type the full copy command. (Example copy http://10.18.101.44/ios.bin flash)";
    $destination_file = read-host "Type the destination file name. (Example: ios.bin)";
    $boot_system_command = read-host "Type the full boot system command. (Example: boot system flash:/ios.bin)";

# Create playbooks
    out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "---" -encoding utf8;

    out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "- name: Upgrade IOS" -encoding utf8 -append;
    out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "  hosts: tempinventory" -encoding utf8 -append;
    out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "  gather_facts: no" -encoding utf8 -append;
    out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "  connection: local" -encoding utf8 -append;
    out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "  vars:" -encoding utf8 -append;
    out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "    ansible_command_timeout: $timeout_seconds" -encoding utf8 -append;
    out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "  tasks:" -encoding utf8 -append;

    out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "  - name: Copy IOS to devices" -encoding utf8 -append;
    out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "    cli_command:" -encoding utf8 -append;
    out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "      command: $copy_command" -encoding utf8 -append;
    out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "      check_all: true" -encoding utf8 -append;
    out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "      prompt:" -encoding utf8 -append;
    out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "        - 'Destination filename [$destination_file]?'" -encoding utf8 -append;
    out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "      answer:" -encoding utf8 -append;
    out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "        - `'$destination_file`'" -encoding utf8 -append;

    out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "  - name: Set boot system cmd on devices" -encoding utf8 -append;
    out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "    ios_command:" -encoding utf8 -append;
    out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "      commands:" -encoding utf8 -append;
    out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "        - configure terminal" -encoding utf8 -append;
    out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "        - no boot system" -encoding utf8 -append;
    out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "        - $boot_system_command" -encoding utf8 -append;
    out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "        - config-register $config_register" -encoding utf8 -append;
    out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "        - end" -encoding utf8 -append;

    out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "  - name: Write-Reload" -encoding utf8 -append;
    out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "    cli_command:" -encoding utf8 -append;
    out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "      command: 'write'" -encoding utf8 -append;
    out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "  - name:" -encoding utf8 -append;
    out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "    cli_command:" -encoding utf8 -append;
    out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "      command: 'reload in $reload_minutes'" -encoding utf8 -append;
    out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "      check_all: True" -encoding utf8 -append;
    out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "      prompt:" -encoding utf8 -append;
    out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "        - 'Confirm'" -encoding utf8 -append;
    out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "      answer:" -encoding utf8 -append;
    out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "        - 'y'" -encoding utf8 -append;

# Create hosts file
    copy-item "hosts_header" "$current_dir\hosts"

    out-file -filepath "$current_dir\hosts" -inputobject "   tempinventory:" -encoding utf8 -append;
    out-file -filepath "$current_dir\hosts" -inputobject "     hosts:" -encoding utf8 -append;

    foreach($device in $devices)
    {
        $location = $device.location;
        $model = $device.model;
        $devicename = $device.devicename;
        $active = $device.active;
        $ip = $device.ip;
        $arg1 = $device.arg1;
        $arg2 = $device.arg2;
        $arg3 = $device.arg3;
        $arg4 = $device.arg4;
        $arg5 = $device.arg5;

        . "$host_cond_loc";

        out-file -filepath "$current_dir\hosts" -inputobject "       $devicename`:" -encoding utf8 -append;
        out-file -filepath "$current_dir\hosts" -inputobject "         ansible_host: $ip" -encoding utf8 -append;
    }

# Check before executing
    write-host "Check before executing."
    start-process -filepath "$textedit_loc" -argumentlist "$current_dir\ansible_temp_task.yaml","$current_dir\hosts"
    pause

# Copy playbook and hosts file to Ansible server
    copy-item "$current_dir\hosts" "\\$ansible_server\ansiblerepo\hosts"
    copy-item "$current_dir\ansible_temp_task.yaml" "\\$ansible_server\ansible\playbooks\ansible_upgrade_ios"

# # Run playbook an Ansible server
    plink "ansibleadmin@$ansible_server" "/var/ansiblerepo/playbooks/ansible_upgrade_ios/ansible_temp_task.sh"

# Copy output back to current directory
    copy-item "\\$ansible_server\ansiblerepo\playbooks\ansible_upgrade_ios\output\*" "$current_dir"

# Show playbook results
    # start-process -filepath "$textedit_loc" -argumentlist "$current_dir\playbook_results.txt"

# # Disable service account
