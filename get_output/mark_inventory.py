#!/usr/bin/env python3

#    Copyright 2023 Anthony Tranquillo

#    This file is part of Jobiation.

#    Jobiation is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

#    Jobiation is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License along with Jobiation.  If not, see <http://www.gnu.org/licenses/>.

# Imports
import sys;
import re;

# Import options file
sys.path.insert(1, '../');
import options;
import functions;
import validations;
import messages;

# Make a list of the first line columns of inventory.csv
flList = functions.getFirstLine(open(options.inventory_file,"r"));

# Get index value of devicename
devicenameIndex = functions.getListIndex(flList,"devicename");

# Get inventory file name from users
new_file_name = input("\nWhat shall be the name of the marked inventory file? ");

# Ask user for the name of the mark column
new_column_name = input("\nWhat shall be the name of the marked column? ");

# Validate new column name
if not re.search(validations.flAllowedChars, new_column_name):
    print("\n!"+new_column_name+messages.badFirstLine);
    sys.exit();

# Create new inventory file
marked_inv_file = open(new_file_name + ".csv","w");

# Open current inventory file
inventory_file = open(options.inventory_file,"r");

# Open mark file
mark_file = open("mark_inventory.txt","r");

# # Create mark list
mark_list = [];

# Populate mark_list[]
for mark in mark_file:
    mark_list.append(mark.strip("\n"));

for inv_line in inventory_file:
    devicename_list = inv_line.split(",");
    devicename = devicename_list[int(devicenameIndex)];
    if devicename == "devicename" or devicename == "skipline":
        marked_inv_file.write(new_column_name+","+inv_line);
    elif devicename in mark_list:
        marked_inv_file.write("1,"+inv_line);
    else:
        marked_inv_file.write("0,"+inv_line);

# Close files
inventory_file.close();
marked_inv_file.close();
mark_file.close();

# Notify user playbook has finished
print("\n\n Your marked inventory file is get_output\\"+new_file_name+".csv\n\n");