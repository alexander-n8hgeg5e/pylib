# -*- coding: utf-8 -*-
# Copyright 2021 Alexander Wilhelmi
# This file is part of pylib.
# 
# pylib is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# pylib is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with pylib.  If not, see <http://www.gnu.org/licenses/>.
# 
# Diese Datei ist Teil von pylib.
# 
# pylib ist Freie Software: Sie können es unter den Bedingungen
# der GNU General Public License, wie von der Free Software Foundation,
# Version 3 der Lizenz oder (nach Ihrer Wahl) jeder neueren
# veröffentlichten Version, weiter verteilen und/oder modifizieren.
# 
# pylib wird in der Hoffnung, dass es nützlich sein wird, aber
# OHNE JEDE GEWÄHRLEISTUNG, bereitgestellt; sogar ohne die implizite
# Gewährleistung der MARKTFÄHIGKEIT oder EIGNUNG FÜR EINEN BESTIMMTEN ZWECK.
# Siehe die GNU General Public License für weitere Details.
# 
# Sie sollten eine Kopie der GNU General Public License zusammen mit diesem
# Programm erhalten haben. Wenn nicht, siehe <https://www.gnu.org/licenses/>.

from os.path import abspath,dirname,normpath,isabs
from subprocess import STDOUT
from subprocess import check_output

def scan_file_and_include(filename):
    """
    needed by scan_file
    """

    # need search path
    search_path = abspath( dirname( filename ))

    # read
    with open(filename,mode='rt') as f:
        lines = f.readlines()
    l=[]
    # strip newlines and empty space
    for i in lines:
        l.append(i.strip())
    lines=l

    # check for include statement prior to shell evaluation
    # and append scanned included files recursively
    # divide lines into 2 lists
    includelist=[]
    l=[]
    for line in lines:
        w = "include"
        if (line[0:len(w)]==w):
            # store rest of line and strip whitespace
            relpath=line[len(w):].strip()
            # append to list with searchpath prepended
            # so it will be a absolute path
            includelist.append( path_add_searchpath( search_path, relpath ))
        else:
            # if it is no include append to fresh include line free list
            # don't add searchpath yet, first shell expansion is needed 
            l.append(line)
    # scan all included files
    for f in includelist:
        l.extend( scan_file_and_include(f) )
    return l

def scan_file(filename):
    """
    Scans a gitpacks file and returns the repo pathes.
    """
    # need search path
    search_path = abspath( dirname( filename ))

    lines=scan_file_and_include( filename )
    # eval shell vars
    l=[]
    for line in lines:
        fish_script= 'echo '+ line
        pythonish_cmd = [ 'fish', '-c' , fish_script  ]
        out=check_output( pythonish_cmd, stderr=STDOUT, shell=False)
        l.append(out.decode(errors='replace').strip())
    return l

def path_at_path( p, searchpath):
    if not isabs(p):
        return abspath( normpath( searchpath ) + '/' + normpath( p ) )
    else:
        return normpath(p)

def pathlist_at_path( l , searchpath ):
    ll=[]
    for i in l:
        ll.append( path_add_searchpath( search_path, i ) )
    return ll

from deprecation import deprecated
@deprecated()
def path_add_searchpath(a,b):
    return path_at_path(b,a)

@deprecated()
def pathlist_add_searchpath(a,b):
    return pathlist_at_path(b,a)
