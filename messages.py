#!/usr/bin/emv python3

#    Copyright 2023 Anthony Tranquillo

#    This file is part of Jobiation.

#    Jobiation is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

#    Jobiation is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License along with Jobiation.  If not, see <http://www.gnu.org/licenses/>.

noHostsHeader = "\nYou need to put a hosts_header file in location specified when you set the use_hosts_header to True in options.py.\n";
noUsername = "\nYou do not have a username set. What username do you want to use? ";
badFirstLine = " - The top line of the inventory can contain numbers, letters, and underscores.\n\nPlease do not use more than 15 characters in any column header.\n\nThe first character should be a letter.\n";
badDeviceName = " - The devicename column can contain numbers, letters, dashes, periods, and underscores.\n\nPlease do not use more than 30 characters in any devicename.\n\nThe first character should be a letter.\n";
badArgNameMsg = " - The argument passed to this script can contain numbers, letters, dashes, periods, and underscores.\n\nPlease do not use more than 30 characters in any arguments to this script.\n\nThe first character should be a letter.\n";
badDictKey = " - Dictionary keys can contain letters, numbers, and underscores. Please do not use more than 15 characters in any dictionary key.\n\nThe first character should be a lower case letter.\n";