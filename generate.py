#!/usr/bin/env python
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

from xbmcaddonbrowser import xbmcaddonbrowser
import fabfile
import settings
from optparse import OptionParser
'''
Parts of the build process

update the git projects
generate content pages from templates
clean publish folder
copy everything over
js concat, min, replace
css concat, min, replace
html min
image optimize
'''

def get_commandline_args():
    parser = OptionParser()

    parser.add_option('-j', '--skip-js', action='store_false', dest='compile_js', default=True,
        help='Don\'t increase javascript build number.')
    parser.add_option('-c', '--skip-css', action='store_false', dest='compile_css', default=True,
        help='Don\'t increase CSS build number.')
    parser.add_option('-r', '--rebuild-images', action='store_true', dest='rebuild_images', default=False,
        help='Rebuild and optimize all images.')
    parser.add_option('-d', '--development', action='store_true', dest='development', default=False,
        help='Publish a development build only. Skips the fabric calls and also keeps media point locally.')
    
    return parser.parse_args()

def main():
    opts, args = get_commandline_args()

    xbmcaddonbrowser.generate_site(
        settings, 
        compile_js=opts.compile_js,
        compile_css=opts.compile_css,
        development=opts.development,

    )

    # run fabric publish
    #if not opts.development:
        #fabfile.publish_build()

if __name__ == '__main__':
    main()
