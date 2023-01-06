#!/usr/bin/emv python3


# def saveFacts(tempfile,facts_module,spaces):
#     tempfile.write(spaces+"playbookfile.write('   - name: gather_facts\\n');\n");
#     tempfile.write(spaces+"playbookfile.write('     " + facts_module + ":\\n');\n");
#     tempfile.write(spaces+"playbookfile.write('     register: factsoutput\\n');\n");

# def saveShowCmd(tempfile,cisco_product_line,showcmd,spaces):
#     tempfile.write(spaces+"playbookfile.write('   - name: run_show_command\\n');\n");
#     tempfile.write(spaces+"playbookfile.write('     " + cisco_product_line + ":\\n');\n");
#     tempfile.write(spaces+"playbookfile.write('       commands: " + showcmd + "\\n');\n");
#     tempfile.write(spaces+"playbookfile.write('     register: showcmd\\n');\n");

# def catFiles():
#     filenames = ["scriptfiles/header.py", "scriptfiles/columns.py", "../host_conditions.py", "scriptfiles/footer.py", "scriptfiles/replacements.py"]
#     with open("scriptfiles/compiled.py", "w") as new_file:
#         for name in filenames:
#             with open(name) as f:
#                 for line in f:
#                     new_file.write(line)
