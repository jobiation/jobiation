
        hostsfile.write("       " + devicename + ":\n");
        hostsfile.write("         ansible_host: " + ip + "\n");

        playbookfile.write("- name: " + devicename + "_pb\n");
        playbookfile.write("  hosts: " + devicename + "\n");
        playbookfile.write("  gather_facts: no\n");
        playbookfile.write("  vars:\n");
        playbookfile.write("    ansible_command_timeout: 30\n");
        playbookfile.write("  tasks:\n");
        playbookfile.write("  - name: " + devicename + "_commands\n");
        playbookfile.write("    ios_commands:\n");
        playbookfile.write("      commands:\n");
