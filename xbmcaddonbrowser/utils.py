# Copyright 2011 Jonathan Beluch
# This file is part of XBMC Addon Browser.
#  
# XBMC Addon Browser is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# XBMC Addon Browser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with XBMC Addon Browser.  If not, see
# <http://www.gnu.org/licenses/>.

from datetime import datetime
import subprocess as s
import os

def read(path):
    with open(path, 'r') as f:
        text = f.read()
    return text

def read_lines(path):
    with open(path, 'r') as f:
        text = f.readlines()
    return text

def read_lines_safe(path):
    try:
        lines = read_lines(path)
    except IOError:
        lines = []
    return lines

def write(fn, contents):
    '''Writes contents to fn.'''
    with open(fn, 'w') as f:
       f.write(contents) 

def list_dirs(basepath, include_hidden=False):
    '''Returns a list of filepaths for directories in a given directory. Ignores 
    directories that begin with a '.'.'''
    dirs = os.listdir(basepath)

    # filter out hidden files like .git, .gitignore
    if not include_hidden:
        dirs = filter(lambda d: not d.startswith('.'), dirs)

    # now build full paths
    dirs = [os.path.join(basepath, d) for d in dirs]

    # filter out files that aren't directories
    dirs = filter(lambda d: os.path.isdir(d), dirs)

    return dirs

def human_datetime(timestamp):
    dt = datetime.fromtimestamp(int(timestamp))
    return dt.strftime('%m/%d/%y %H:%M')

def dict_from_file_factory(read_func=read_lines, sep=' '):
    def dict_from_file(filename):
        lines = read_func(filename)
        pairs = [line.strip().split(sep, 1) for line in lines]
        pairs = filter(lambda p: len(p) == 2, pairs)
        return dict(pairs)
    return dict_from_file


def dict_to_file_factory(sep=' '):
    def dict_to_file(filename, dictionary):
        with open(filename, 'w') as f:
            f.write('\n'.join(sep.join([k, v]) for k, v in dictionary.items()))
    return dict_to_file

dict_from_file = dict_from_file_factory()
dict_to_file = dict_to_file_factory()
get_hash_filenames = dict_from_file_factory(read_func=read_lines_safe, sep=' ')
write_hash_filenames = dict_to_file_factory(sep=' ')

def command(command_string):
    p = s.Popen(command_string, stdout=s.PIPE, stderr=s.PIPE, shell=True)
    stdout, stderr = p.communicate()
    return stdout, stderr
