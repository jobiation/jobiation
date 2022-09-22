#!/usr/bin/env python3

# https://www.thegeekstuff.com/2014/07/python-regex-examples/

import sys;
import mmap;
import re;


with open('notes.txt', 'r') as file1:
    content = file1.read()
match = re.search('(interface GigabitEthernet0/0/0(.*\n){1,5}ip address)(.*\n){1,6}interface GigabitEthernet0/0/1', content)
if match:
  print("match");
else:
  print("no match");
    # print('Found a match starting on line', content.count('\n', 0, match.start()))
    
    
""" Stuff to go over.* means match anything
^ and $
\n
| means or
? means optional
{n,m} means between n and m
() group together
literal strings
\ is escape charater. Also tell them which characters they need to escape in literals
r is raw string
know what kind of line endings you have
"""

# file1 = open('notes.txt','r');
# result = re.search("encoding", str(file1));
# print(result);

sys.exit();


# ############################# Efficient way

# file1 = open('notes.txt');


# with file1 as file, \
#      mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as s:
#      if s.find(b'banner') != -1:
#         print('found it')

# file1.close();

# sys.exit();

######################regex



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


# Notes: Multiline strings can be assigned to a variable with 3 quotes