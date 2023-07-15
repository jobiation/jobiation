#!/usr/bin/emv python3

#    Copyright 2023 Anthony Tranquillo

#    This file is part of Jobiation.

#    Jobiation is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

#    Jobiation is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License along with Jobiation.  If not, see <http://www.gnu.org/licenses/>.

def saveFacts(tempfile,facts_output,spaces):
    tempfile.write(spaces+"playbookfile.write('   - name: gather_facts\\n');\n");
    tempfile.write(spaces+"playbookfile.write('     " + facts_output + ":\\n');\n");
    tempfile.write(spaces+"playbookfile.write('     register: facts_output\\n');\n");

def saveShowCmd(tempfile,cisco_command_type,showcmd,spaces):
    tempfile.write(spaces+"playbookfile.write('   - name: run_show_command\\n');\n");
    tempfile.write(spaces+"playbookfile.write('     " + cisco_command_type + ":\\n');\n");
    tempfile.write(spaces+"playbookfile.write('       commands: " + showcmd + "\\n');\n");
    tempfile.write(spaces+"playbookfile.write('     register: showcmd\\n');\n");
