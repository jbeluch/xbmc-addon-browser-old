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

from jinja2 import Environment, PackageLoader, FileSystemLoader
from datetime import datetime as dt
from languagecodes import LANGUAGES

class Website(object):
    def __init__(self, template_dir):
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def render_addons_page(self, addon_contexts, development=False):
        addons_tpl = self.env.get_template('addons.html')
        updated = dt.now().strftime('%B %d, %Y %X UTC')

        # Get a list of languages found in the given addon_contexts
        languages_in_use = []
        for addon in addon_contexts:
            #if 'descriptions' in addon.keys():
            if addon.descriptions:
                languages_in_use += addon.descriptions.keys()

        languages_in_use = set(languages_in_use)
        pairs = [(lang, LANGUAGES.get(lang, lang)) for lang in languages_in_use]
        # Sort by display name not by language code
        language_pairs = sorted(pairs, key=lambda p: p[1])

        # Quick fix to support proper timezones since my server is UTC.
        updated_iso = '%sZ' % dt.now().isoformat()

        output = addons_tpl.render(addons=addon_contexts, 
            updated=updated, 
            updated_iso=updated_iso, 
            languages=LANGUAGES,
            language_pairs=language_pairs,
            development=development,
        )

        return output

    def render_about_page(self):
        about_tpl = self.env.get_template('about.html')
        output = about_tpl.render()

        return output
    
