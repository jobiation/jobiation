#!/usr/bin/env python3

# ############################# Efficient way

import sys;
import mmap;
import re

# file1 = open('notes.txt');

# with file1 as file, \
#      mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as s:
#      if s.find(b'banner') != -1:
#         print('found it')

# file1.close();

# sys.exit();


######################regex

re.compile(r"^(.+)\n((?:\n.+)+)", re.MULTILINE)

# opening and reading the file
with open('notes.txt') as fh:
  string = fh.readlines()
    
# declaring the regex pattern for IP addresses 
#pattern =re.compile("((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)")
# ipandwildcard =re.compile("((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\ ((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)");
# ipaddress24 =re.compile("ip address ((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?) 255.255.255.0")
pattern =re.compile("([0-2]?[0-9]?[0-9])\.([0-2]?[0-9]?[0-9])\.([0-2]?[0-9]?[0-9])\.([0-2]?[0-9]?[0-9])$")


# extracting the IP addresses
for line in string:
    line = line.rstrip();
    result = pattern.search(line);
    print(result);


######################In efficient way



# file1 = open('notes.txt');
# with file1 as f:
#     if 'banner' in f.read():
#         print("true")

# file1.close();

# sys.exit();
