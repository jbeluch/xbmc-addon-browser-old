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

import git
from addon import Addon
from image import Image, optimize_pngs
from template import Website
from build import update_js_refs, update_css_refs, minify, concat
import os
import shutil
from utils import list_dirs, get_hash_filenames, write_hash_filenames, dict_from_file, dict_to_file

def get_addons(repo):
    '''Returns a list of addon objects for a given repo object.'''
    addon_paths = list_dirs(repo.path)
    return [Addon(repo, addon_path) for addon_path in addon_paths]

def copy_icons(addons, dest):
    '''Copies an addons icon to the destination folder. An md5 is checked for each icon. If the md5 appears
    in the cached list, the icon will not be copied over, its web_basename will simply be changed to point
    to the existing file. Returns a list of newly copied icons, so they can be opitimized.'''
    icons_dir = os.path.join(dest, 'icons')
    md5fn = os.path.join(icons_dir, '.md5s')
    icons = get_hash_filenames(md5fn) # Master dict of all icons
    current_icons = {} # Keeps track of icons in use during this build
    new_icon_fns = [] # Keeps track of icons that were copied over


    # Only process addons with an icon
    addons = filter(lambda a: a.icon, addons)

    for addon in addons:
        icon = addon.icon

        if icon.md5 not in icons.keys():
            # Cache miss, so we copy the icon to the destination and update our current md5s dict
            icon.copy_to(os.path.join(icons_dir, icon.web_basename))
            icons[icon.md5] = icon.web_basename
            # Keep track of newly added icons so we can later optimize them
            new_icon_fns.append(icon.web_basename)
        else:
            # We already have a copy of the icon, simply update our icons web_basename to point to the existing icon
            icon.web_basename = icons[icon.md5]

        current_icons[icon.md5] = icon.web_basename

    # Now delete any old icons that are no longer in use
    old_icon_fns = set(icons.values()) - set(current_icons.values())
    map(os.remove, old_icon_fns)

    # Write the current filenames and hashes back to disk
    write_hash_filenames(md5fn, current_icons)

    # Return full filenames
    return [os.path.join(icons_dir, fn) for fn in new_icon_fns]

def generate_html(template_path, dest, addon, development=False):
    site = Website(template_path)
    pages = [
        ('index.html', site.render_addons_page(addon, development).encode('utf-8')),
        ('about.html', site.render_about_page()),
    ]

    output_fns = []
    for fn, output in pages:
        output_fns.append(os.path.join(dest, fn))
        with open(os.path.join(dest, fn), 'w') as f:
            f.write(output)
    return output_fns

def get_new_build_numbers(fn):
    d = dict_from_file(fn)
    return int(d['js']), int(d['css'])

def write_current_build_numbers(fn, js, css):
    d = {'js': str(js), 'css': str(css)}
    dict_to_file(fn, d)

def generate_site(settings, compile_js=True, compile_css=True, development=False):
    # Delete deploy_old if it exists and move current deploy to deploy_old
    try:
        shutil.rmtree('%s_old' % settings.DEPLOY_DIR)
    except OSError:
        pass
    try:
        shutil.move(settings.DEPLOY_DIR, '%s_old' % settings.DEPLOY_DIR)
    except IOError, e:
        print 'Error backing up the deploy directory or it doesn\'t exist.'

    # Create new deploy directory
    os.mkdir(settings.DEPLOY_DIR)

    # Update git repos listed in the settings files
    repos = map(git.Repository, settings.REPOS)
    # updated will be True if at least one repo was updated.
    updated = any([repo.pull() for repo in repos])
    # Currently not using updated. Potentially could skip the regeneration if nothing was updated.
    # However, the last-updated timestamps should at least be updated. Just easier to regenerate everything
    # at this point.

    # Build a list of addons from all of the available repos
    addons = []
    for r in repos:
        addons += get_addons(r)
        
    # For each addon, copy its icon to the proper folder assuming its not already there and optimized.
    new_icons = copy_icons(addons, settings.IMG_PATH)

    # Optimize only new images
    optimize_pngs(new_icons)

    # Copy over the media folder, contains js, css, images
    shutil.copytree(settings.MEDIA_PATH, os.path.join(settings.DEPLOY_DIR, 'media'))

    # Generate HTML
    generate_html(settings.TEMPLATES_PATH, settings.DEPLOY_DIR, addons, development=development)

    # Before proceding with js and css, get current build numbers for each
    js_build_number, css_build_number = get_new_build_numbers(settings.BUILD_INFO)

    # Concat and minify js
    if compile_js:
        js_build_number += 1
    js_fn = concat(os.path.join(settings.DEPLOY_DIR, 'media', 'js'), 'js', 'scripts-%03d-min.js' % js_build_number, ignore=['libs'])
    minify(js_fn)
    update_js_refs(settings.DEPLOY_DIR, js_fn)

    # Concat and minify css
    if compile_css:
        css_build_number += 1
    css_fn = concat(os.path.join(settings.DEPLOY_DIR, 'media', 'css'), 'css', 'style-%03d-min.css' % css_build_number)
    minify(css_fn)
    update_css_refs(settings.DEPLOY_DIR, css_fn)

    write_current_build_numbers(settings.BUILD_INFO, js_build_number, css_build_number)

    # Minify the HTML
    # Currently minify_html_bin is not working... it outputs a 0 byte file :(
    #minify_html(settings.DEPLOY_DIR)
