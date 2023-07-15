#!/usr/bin/emv python3

#    Copyright 2023 Anthony Tranquillo

#    This file is part of Jobiation.

#    Jobiation is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

#    Jobiation is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License along with Jobiation.  If not, see <http://www.gnu.org/licenses/>.

import re;

flAllowedChars =re.compile("^[a-zA-Z]([0-9a-zA-Z_]){1,14}$");

dictAllowedChars =re.compile("^[a-z]([a-zA-Z0-9_]){1,14}$");

numericreg = re.compile("^[0-9]{1,4}$");

devicenameAllowed =re.compile("^[a-zA-Z]([0-9a-zA-Z_.-]){1,29}$");

argNameAllowed =re.compile("^[a-zA-Z]([0-9a-zA-Z_.-]){1,29}$");

