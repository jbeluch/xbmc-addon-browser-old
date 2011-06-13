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
import os
from utils import command

def preserve_cwd(fn):
    '''A wrapper to preserve the current working directory. Restores the cwd after the wrapped
    fucntion has exited.'''
    def wrapped(*args, **kwargs):
        cwd = os.getcwd()
        ret = fn(*args, **kwargs)
        os.chdir(cwd)
        return ret
    return wrapped

class Repository(object):
    def __init__(self, path):
        self.path = path
        self.pretty_log_lines = None

    def clone(self):
        # Clone the repo, todo
        raise NotImplementedError
        
    @preserve_cwd
    def pull(self):
        '''Executes a git pull. Returns True if there were updates, False
        if the repo is already up-to-date.'''
        print 'Executing \'git pull\' for %s' % self.path
        os.chdir(self.path)
        stdout, stderr = git_command('pull')
        lines = stdout.splitlines()
        if len(lines) == 1 and lines[0] == 'Already up-to-date.':
            # Already up-to-date.
            return False
        return True

    def pretty_log(self):
        '''Returns the output of git log, printing the unix timestamp of the commit and the subject.'''
        if not self.pretty_log_lines:
            os.chdir(self.path)
            stdout, stderr = git_command('log --format="format:%at %s"')
            self.pretty_log_lines = stdout.splitlines()
        return self.pretty_log_lines

def git_command(command_str):
    return command('git %s' % command_str)
