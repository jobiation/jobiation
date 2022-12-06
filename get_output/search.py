#!/usr/bin/env python3

# # Define the directory
# rootdir = "";

# if rootdir == "":
#     print("\nrootdir is null so I will search the first directory in the jobs folder. If it does not exist I will do a new pull.");
# elif rootdir == "prompt":
#     print("\nWhat is the name of the directory you would like to use as the root directory. If blank I will do a new pull");
# else:
#     print("\nThere is a value specified in rootdir so I will use that");

## Define the jobs exports in the following format:
## directoryname : command
showcmd_exports = {
    # "showrun":"show running-config",
    # "showver":"show version"
    }

## Define the facts module to use for the export.
## This will be the name of the directory that stores the facts exports
export_facts = "cisco.ios.ios_facts"; # Specify the directory name or leave blank to not collect ios_facts

## Define search objects
## This is optional.
## You can write your search criteria stored in variables here and then reference the variables in the searches dictionary.
## You can also not define any variables in this section and specify your search criteria in the searches dictionary.
my_search_object = "17.3.4";

## Define your searches in the following format:
## columnname : directoryname!!searchcriteria
searches = {
    
    ## Example search that searches the show run output for the ntp server command.
    "has_ntp":"showrun!!ntp server 10.1.1.1",

    "has_tacacs":"showrun!!ip tacacs server isetacacs",
    "needs_upgrade":"showver!!"+my_search_object,
    "has8interfaces":"ios_facts!!GigabitEthernet0/0/7"
    }

# ## Loop through searches dictionary
# for search in searches:
#     dictval = searches[search].split("!!");
#     dirname = dictval[0];
#     criteria = dictval[1];

#     print("\n");
#     print("- This search map will look for '" + criteria + "' inside the '" + dirname + "' directory and store the result in the column '" + search + "'.");
