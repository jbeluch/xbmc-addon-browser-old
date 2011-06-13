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
import re
from utils import command, write, read
#from jsmin import jsmin
#from cssmin import cssmin

js_filter = lambda fn: fn.endswith('.js')
html_filter = lambda fn: fn.endswith('.html')
css_filter = lambda fn: fn.endswith('.css')
FILTERS = {
    'css': css_filter,
    'html': html_filter,
    'js': js_filter,
}

# Currently not working - minify_html outputs a 0 byte file
#def minify_html(basepath):
    #fns = get_all_fns(basepath, custom_filter=html_filter)
    #map(minify, fns)

def minify(fn):
    filetypes = ['css', 'js', 'html']
    _, ending = fn.rsplit('.', 1)
    assert ending in filetypes

    minifier = os.path.join(os.path.dirname(__file__), 'tools', 'minify_%s_bin' % ending)
    print 'Minifying %s' % fn
    stdout, stderr = command('%s %s %s' % (minifier, fn, fn))
    
def concat(basepath, filetype, output_fn, ignore=None):
    assert filetype in FILTERS.keys()
    input_fns = get_all_fns(basepath, ignore, custom_filter=FILTERS[filetype])
    output = concat_files(input_fns)
    for fn in input_fns:
        print 'Including %s in %s output.' % (fn, filetype)

    # Write the new scripts file
    output_fn = os.path.join(basepath, output_fn)
    write(output_fn, output)

    # Remove all *.<filetype> files that we included in the new output file
    map(os.remove, input_fns)

    return output_fn

def concat_files(fns):
    '''Returns the concatenated output of files in fns.'''
    contents_list = map(read, fns)
    output = '\n'.join(contents_list)
    return output

def replace_in_file(fn, pattern, repl):
    '''Calls re.sub(pattern, repl) on a file's contens and writes the resulting output
    back to the same file.'''
    contents = read(fn)
    output = re.sub(pattern, repl, contents)
    write(fn, output)

def update_css_refs(basepath, css_fn):
    html_files = get_all_fns(basepath, custom_filter=html_filter)
    LB = '<!-- css concatenated and minified -->'
    RB = '<!-- end css -->'
    p = re.compile('%s.+?%s' % (LB, RB), re.DOTALL)
    rel_css_path = os.path.relpath(css_fn, basepath)
    new = '<link rel="stylesheet" href="%s">' % rel_css_path

    for f in html_files:
        print 'Updating css references in %s' % f
        replace_in_file(f, p, new)

def update_js_refs(basepath, js_fn):
    html_files = get_all_fns(basepath, custom_filter=html_filter)
    LB = '<!-- scripts concatenated and minified -->'
    RB = '<!-- end scripts -->'
    p = re.compile('%s.+?%s' % (LB, RB), re.DOTALL)
    rel_js_path = os.path.relpath(js_fn, basepath)
    new = '<script src="%s"></script>' % rel_js_path

    for f in html_files:
        print 'Updating js references in %s' % f
        replace_in_file(f, p, new)

def get_all_fns(basepath, ignore=None, custom_filter=None):
    '''Returns a list of filenames for *.js files underneath a given directory. Will
    honor the given ignore list to ignore folders and files specified.'''

    if ignore is None:
        ignore = []
    prune = lambda fs: filter(lambda f: f not in ignore, fs)

    fns = []
    for root, dirs, files in os.walk(basepath, topdown=True):
        # Filter directories left to visit and remove any that are in the ignore list.
        dirs[:] = prune(dirs)

        # Filter files and remove any that are in the ignore list. Also filter by *.js
        files = prune(files)
        if custom_filter:
            files = filter(custom_filter, files)
        full_fns = [os.path.join(root, fn) for fn in files]
        fns.extend(full_fns)

    return fns
