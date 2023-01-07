#!/usr/bin/emv python3

import sys
import shutil

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

def abortPlaybook(current_dir,message):
    print(message);
    shutil.rmtree(current_dir);
    sys.exit();

def getFirstLine(inventoryfile):
    with inventoryfile as invrow:
        firstline = invrow.readline();
    inventoryfile.close();
    return firstline.split(",");
