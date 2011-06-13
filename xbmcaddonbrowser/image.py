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
import hashlib
import shutil
import os
import subprocess as s
from utils import command

class Image(object):
    def __init__(self, path, base_fn):
        self.path = path
        self._md5 = self._generate_md5(self.path)
        self._web_basename = '%s.png' % base_fn

    @property
    def web_basename(self):
        return self._web_basename

    @web_basename.setter
    def web_basename(self, basename):
        self._web_basename = basename

    @property
    def relative_uri(self):
        return 'media/img/icons/%s' % self.web_basename

    @property
    def uri(self):
        return 'http://%s.xbmcaddonbrowser.com/img/icons/%s' % (self.web_basename[0], self.web_basename)

    @property
    def md5(self):
        return self._md5

    def _generate_md5(self, path):
        with open(path, 'rb') as f:
            h = hashlib.md5(f.read())
        return h.hexdigest()

    def copy_to(self, dest_fn):
        shutil.copy(self.path, dest_fn)

class ImageSet(set):
    def __init__(self, md5_filename):
        self.fn = md5_filename

    def update_from_disk(self):
        # get old md5s if they exist
        try:
            with open(self.fn) as f:
                lines = f.readlines()
        except IOError:
            self.md5s = {}
        else:
            self.md5s = dict((line.strip().split(' ', 1) for line in lines))

    def write_hash_filenames(self):
        with open(self.fn, 'w') as f:
            f.write('\n'.join('%s %s' % (k, v) for k, v in md5s.items()))

def optimize_pngs(fns):
    '''Takes a root directory path and a list of *.png filenames and replaces each file with
    an optimzed version.'''
    cwd = os.path.dirname(__file__)
    optimize_bin = os.path.join(cwd, 'tools', 'optimize_image_bin')

    for fn in fns:
        print 'Optimizing %s' % fn
        stdout, stderr = command('%s %s %s' % (optimize_bin, fn, fn))
        
def optimize_images(path):
    for root, dirs, files in os.walk(path):
        pngs = filter(lambda f: f.endswith('.png'), files)
        optimize_pngs([os.path.join(root, fn) for fn in pngs])
        
