#!/usr/bin/emv python3

def buildHosts(interperter, connection, os, port, user):
    hostsfile = open("tmp/hosts","w");
    hostsfile.write("---\n");
    hostsfile.write("all:\n");   
    hostsfile.write(" vars:\n");
    hostsfile.write("  ansible_python_interpreter: " + interperter + "\n");
    hostsfile.write("  ansible_connection: " + connection + "\n");
    hostsfile.write("  ansible_network_os: " + os + "\n");
    hostsfile.write("  ansible_port: " + port + "\n");
    hostsfile.write("  ansible_user: " + user + "\n");
    hostsfile.write(" children:\n");
    hostsfile.write("   tempinventory:\n");
    hostsfile.write("     hosts:\n");
    # hostsfile.write("\n");

    hostsfile.close();

def catFiles():
    filenames = ["scriptfiles/header.py", "scriptfiles/columns.py", "../host_conditions.py", "scriptfiles/footer.py"]
    with open("scriptfiles/compiled.py", "w+") as new_file:
        for name in filenames:
            with open(name) as f:
                for line in f:
                    new_file.write(line)