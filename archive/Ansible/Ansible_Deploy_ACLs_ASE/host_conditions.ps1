# Skiplines and break
    if("$devicename" -eq "skipline"){continue;}
    if("$devicename" -eq "break"){break;}

# Note that multiple if statements work as a logical AND

# Only perform action on active nodes
    if("$arg1" -eq "1"){}else{continue;}

# Match the devices on which you want to perform action
    # if("$arg1" -eq "1"){}else{continue;}