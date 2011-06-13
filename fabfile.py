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

from fabric.api import *
import os
import fabric.contrib.project as project

PROD = 'localhost'
LOCAL = 'localhost'
DEST_PATH = '/www/xbmcaddonbrowser.com/'
ROOT_PATH = os.path.abspath(os.path.dirname(__file__))
DEPLOY_PATH = os.path.join(ROOT_PATH, 'deploy')

#@hosts(LOCAL)

@hosts(PROD)
def publish():
    project.rsync_project(
        remote_dir=DEST_PATH,
        local_dir=DEPLOY_PATH.rstrip('/') + '/',
        delete=True
    )

def publish_build():
    env.hosts.append(PROD)
    env.host_string = 'jon@localhost:22'
    env.port = 22
    env.user = 'jon'
    env.host = PROD

    project.rsync_project(
        remote_dir=DEST_PATH,
        local_dir=DEPLOY_PATH.rstrip('/') + '/',
        delete=True,
        # use checksum for now instead of date/time
        # since the last modified date currently changes every time 
        # we run ./generator.py
        extra_opts='-c --exclude .git/',
    )
