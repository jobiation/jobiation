
        print(devicename);

        hostsfile.write("       " + devicename + ":\n");
        hostsfile.write("         ansible_host: " + ip + "\n");

# Close files
# playbookfile.close();
devicesfile.close();
hostsfile.close();