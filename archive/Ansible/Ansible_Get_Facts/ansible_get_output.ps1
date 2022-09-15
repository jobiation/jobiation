
# Enable service account

# Set variables
    $ansible_server = "ansible";
    $devices_file = "..\devices.csv";
    $host_conditions_file = "..\host_conditions.ps1"; # Hosts conditions location
    $config_conditions = Import-CSV "config_conditions.txt";
    $textedit_loc = "C:\Users\me\AppData\Local\Programs\Microsoft VS Code\Code.exe";

# Remove files in the output folder
    remove-item "\\$ansible_server\ansiblerepo\playbooks\ansible_get_output\output\*"

# Get command from the user
    $command = read-host "Command from which you want output? "; 

# Import devices.csv and commands.txg
    $devices = Import-CSV $devices_file;

# Create a directory for the files
    $current_time=get-date -uformat %Y%m%d_%H%M%S
    $current_dir = ".\playbooks\$current_time";
    mkdir $current_dir;

# Create playbooks
    out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "---" -encoding utf8;

        # $devicename = $device.devicename;

        out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "- name: Get_Output" -encoding utf8 -append;
        out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "  hosts: tempinventory" -encoding utf8 -append;
        out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "  gather_facts: no" -encoding utf8 -append;
        out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "  connection: local" -encoding utf8 -append;
        out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "  vars:" -encoding utf8 -append;
        out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "    ansible_command_timeout: 30" -encoding utf8 -append;
        out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "  tasks:" -encoding utf8 -append;
        out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "  - name: run_show_command" -encoding utf8 -append;
        out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "    ios_command:" -encoding utf8 -append;
        out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "      commands: $command" -encoding utf8 -append;
        out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "    register: output" -encoding utf8 -append;
        out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "  - name: show_output" -encoding utf8 -append;
        out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "    debug:" -encoding utf8 -append;
        out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "      var: output.stdout" -encoding utf8 -append;
        out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "  - name: copy_output_to_file" -encoding utf8 -append;
        out-file -filepath "$current_dir\ansible_temp_task.yaml" -inputobject "    copy: content=`"{{ output.stdout[0] }}`" dest=`"/var/ansiblerepo/playbooks/ansible_get_output/output/{{ inventory_hostname }}.txt`"" -encoding utf8 -append;

# Create hosts file
    copy-item "hosts_header" "$current_dir\hosts"

    out-file -filepath "$current_dir\hosts" -inputobject "   tempinventory:" -encoding utf8 -append;
    out-file -filepath "$current_dir\hosts" -inputobject "     hosts:" -encoding utf8 -append;

    foreach($device in $devices)
    {
        $devicename = $device.devicename;
        $ip = $device.ip;
        $active = $device.active;
        $location = $device.location;
        $model = $device.model;
        $arg1 = $device.arg1;
        $arg2 = $device.arg2;
        $arg3 = $device.arg3;
        $arg4 = $device.arg4;
        $arg5 = $device.arg5;

        . "$host_conditions_file";

        out-file -filepath "$current_dir\hosts" -inputobject "       $devicename`:" -encoding utf8 -append;
        out-file -filepath "$current_dir\hosts" -inputobject "         ansible_host: $ip" -encoding utf8 -append;
    }

# Copy playbook and hosts file to Ansible server
    copy-item "$current_dir\hosts" "\\$ansible_server\ansiblerepo"
    copy-item "$current_dir\ansible_temp_task.yaml" "\\$ansible_server\ansiblerepo\playbooks\ansible_get_output"

## Pause to check
    write-host "";
    write-host "Check before executing?";
    write-host "";
    start-process -filepath "$textedit_loc" -argumentlist "$current_dir\ansible_temp_task.yaml","$current_dir\hosts"
    pause

# # Run playbook an Ansible server
    plink "ansibleadmin@$ansible_server" "/var/ansiblerepo/playbooks/ansible_get_output/ansible_temp_task.sh"

# Copy output back to current directory
    copy-item "\\$ansible_server\ansiblerepo\playbooks\ansible_get_output\output\*" "$current_dir"

# Check conditions
    out-file -filepath "$current_dir\results.csv" -inputobject "`"Device Name`",`"" -encoding utf8 -nonewline;

    foreach($condition in $config_conditions)
    {
        $cond = $condition.condition;
        out-file -filepath "$current_dir\results.csv" -inputobject "$cond`",`"" -encoding utf8  -append -nonewline;
    }

    out-file -filepath "$current_dir\results.csv" -inputobject "`"" -encoding utf8  -append;

    foreach($device in $devices)
    {
        $devicename = $device.devicename;
        $ip = $device.ip;
        $active = $device.active;
        $location = $device.location;
        $model = $device.model;
        $arg1 = $device.arg1;
        $arg2 = $device.arg2;
        $arg3 = $device.arg3;
        $arg4 = $device.arg4;
        $arg5 = $device.arg5;

        . "$host_conditions_file";

        out-file -filepath "$current_dir\results.csv" -inputobject "`"$devicename`",`"" -encoding utf8 -append -nonewline;

        foreach($condition in $config_conditions)
        {
            if((test-path "$current_dir\$devicename.txt"))
            {
                $cond = $condition.condition;
                if(Get-ChildItem -Path "$current_dir\$devicename.txt" | Select-String -Pattern "$cond")
                {
                    write-host "Matches";
                    out-file -filepath "$current_dir\results.csv" -inputobject "1`",`"" -encoding utf8  -append -nonewline;
                }
                else
                {
                    write-host "Does not match --- $cond --- $current_dir\$devicename.txt";
                    out-file -filepath "$current_dir\results.csv" -inputobject "0_no_match`",`"" -encoding utf8  -append -nonewline;
                }
            }
            else
            {
                out-file -filepath "$current_dir\results.csv" -inputobject "0_Unavailable`",`"" -encoding utf8  -append -nonewline;
            }  
        }
        
        out-file -filepath "$current_dir\results.csv" -inputobject "`"" -encoding utf8  -append;
    }

# Disable service account
