        for cmd in commandsfile:
            repstr = cmd;
            repstr = repstr.replace('!devicename', devicename);
            repstr = repstr.replace('!arg1', arg1);
            repstr = repstr.replace('!arg2', arg2);
            playbookfile.write('        - ' + repstr);
inventoryfile.close();
hostsfile.close();
playbookfile.close();
commandsfile.close();