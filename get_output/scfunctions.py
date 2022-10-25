#!/usr/bin/emv python3

# def reloadIn(tempfile,reload_in, spaces):
#     tempfile.write(spaces+"playbookfile.write('   - name: Write\\n');\n");
#     tempfile.write(spaces+"playbookfile.write('     cli_command:\\n');\n");
#     tempfile.write(spaces+"playbookfile.write('       command: \"write\"\\n');\n");
#     tempfile.write(spaces+"playbookfile.write('   - name: Reload\\n');\n");
#     tempfile.write(spaces+"playbookfile.write('     cli_command:\\n');\n");
#     tempfile.write(spaces+"playbookfile.write('       command: \"reload in " + str(reload_in) + "\"\\n');\n");
#     tempfile.write(spaces+"playbookfile.write('       check_all: True\\n');\n");
#     tempfile.write(spaces+"playbookfile.write('       prompt:\\n');\n");
#     tempfile.write(spaces+"playbookfile.write('         - \"Confirm\"\\n');\n");
#     tempfile.write(spaces+"playbookfile.write('       answer:\\n');\n");
#     tempfile.write(spaces+"playbookfile.write('         - \"y\"\\n');\n");

def saveFacts(tempfile,facts_module,current_dir):
    tempfile.write("playbookfile.write('   - name: gather_facts\\n');\n");
    tempfile.write("playbookfile.write('     " + facts_module + ":\\n');\n");
    tempfile.write("playbookfile.write('     register: jobiation_facts\\n');\n");
    tempfile.write("playbookfile.write('   - name: copy_output_to_file\\n');\n");
    tempfile.write("playbookfile.write('     copy: content=\"{{ jobiation_facts }}\" dest=\"" + current_dir + "/{{ inventory_hostname }}_facts.txt\"\\n');\n");

def saveShowCmd(tempfile,cisco_product_line,showcmd,current_dir):
    tempfile.write("playbookfile.write('   - name: run_show_command\\n');\n");
    tempfile.write("playbookfile.write('     " + cisco_product_line + ":\\n');\n");
    tempfile.write("playbookfile.write('       commands: " + showcmd + "\\n');\n");
    tempfile.write("playbookfile.write('     register: jobiation_showcmd\\n');\n");
    tempfile.write("playbookfile.write('   - name: copy_output_to_file\\n');\n");
    tempfile.write("playbookfile.write('     copy: content=\"{{ jobiation_showcmd.stdout[0] }}\" dest=\"" + current_dir + "/{{ inventory_hostname }}_showcmd.txt\"\\n');\n");

# def catFiles():
#     filenames = ["scriptfiles/header.py", "scriptfiles/columns.py", "../host_conditions.py", "scriptfiles/footer.py", "scriptfiles/replacements.py"]
#     with open("scriptfiles/compiled.py", "w") as new_file:
#         for name in filenames:
#             with open(name) as f:
#                 for line in f:
#                     new_file.write(line)
