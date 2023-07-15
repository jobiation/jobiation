#!/usr/bin/emv python3

#    Copyright 2023 Anthony Tranquillo

#    This file is part of Jobiation.

#    Jobiation is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

#    Jobiation is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License along with Jobiation.  If not, see <http://www.gnu.org/licenses/>.

import os;
import re;

def saveFacts(tempfile,facts_module,current_dir):
    tempfile.write("playbookfile.write('   - name: gather_facts\\n');\n");
    tempfile.write("playbookfile.write('     " + facts_module + ":\\n');\n");
    tempfile.write("playbookfile.write('     register: jobiation_facts\\n');\n");
    tempfile.write("playbookfile.write('   - name: copy_output_to_file\\n');\n");
    tempfile.write("playbookfile.write('     copy: content=\"{{ jobiation_facts }}\" dest=\"" + current_dir + "/facts/{{ inventory_hostname }}_facts.json\"\\n');\n");

def saveShowCmd(tempfile,cisco_command_type,showcmd,cmdname,current_dir):
    tempfile.write("playbookfile.write('   - name: " + cmdname + "\\n');\n");
    tempfile.write("playbookfile.write('     " + cisco_command_type + ":\\n');\n");
    tempfile.write("playbookfile.write('       commands: " + showcmd + "\\n');\n");
    tempfile.write("playbookfile.write('     register: " + cmdname + "\\n');\n");
    tempfile.write("playbookfile.write('   - name: copy_output_to_file\\n');\n");
    tempfile.write("playbookfile.write('     copy: content=\"{{ " + cmdname + ".stdout[0] }}\" dest=\"" + current_dir + "/" + cmdname + "/{{ inventory_hostname }}_" + cmdname + ".txt\"\\n');\n");

def cleanFile(cmdfile,cmds_to_remove):
    cmds_to_remove_list = cmds_to_remove.split("!!");
    with open(cmdfile, "r") as srcfile:
        with open("tmp/cleanfiletemp.txt", "w") as tempfile:
            for line in srcfile:
                writeline = 1;
                for badline in cmds_to_remove_list:
                    if re.search(badline,line.strip("\n")):
                        writeline = 0;
                if writeline == 1:
                    tempfile.write(line);
        os.replace('tmp/cleanfiletemp.txt',cmdfile);
        tempfile.close();
    srcfile.close();
