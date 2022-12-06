#!/usr/bin/emv python3

def saveFacts(tempfile,facts_module,current_dir):
    tempfile.write("playbookfile.write('   - name: gather_facts\\n');\n");
    tempfile.write("playbookfile.write('     " + facts_module + ":\\n');\n");
    tempfile.write("playbookfile.write('     register: jobiation_facts\\n');\n");
    tempfile.write("playbookfile.write('   - name: copy_output_to_file\\n');\n");
    tempfile.write("playbookfile.write('     copy: content=\"{{ jobiation_facts }}\" dest=\"" + current_dir + "/facts/{{ inventory_hostname }}_facts.txt\"\\n');\n");

def saveShowCmd(tempfile,cisco_product_line,showcmd,cmdname,current_dir):
    tempfile.write("playbookfile.write('   - name: " + cmdname + "\\n');\n");
    tempfile.write("playbookfile.write('     " + cisco_product_line + ":\\n');\n");
    tempfile.write("playbookfile.write('       commands: " + showcmd + "\\n');\n");
    tempfile.write("playbookfile.write('     register: " + cmdname + "\\n');\n");
    tempfile.write("playbookfile.write('   - name: copy_output_to_file\\n');\n");
    tempfile.write("playbookfile.write('     copy: content=\"{{ " + cmdname + ".stdout[0] }}\" dest=\"" + current_dir + "/" + cmdname + "/{{ inventory_hostname }}_" + cmdname + ".txt\"\\n');\n");

# def catFiles():
#     filenames = ["scriptfiles/header.py", "scriptfiles/columns.py", "../host_conditions.py", "scriptfiles/footer.py", "scriptfiles/replacements.py"]
#     with open("scriptfiles/compiled.py", "w") as new_file:
#         for name in filenames:
#             with open(name) as f:
#                 for line in f:
#                     new_file.write(line)
