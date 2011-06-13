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
from xml.etree import ElementTree as ET
from BeautifulSoup import BeautifulStoneSoup as BSS
from datetime import datetime
from xbmcforum import get_member_url
from languagecodes import LANGUAGES
from image import Image
import jinja2
from jinja2 import escape as e
from utils import read, human_datetime

GITWEB_URL_PATTERN = 'http://xbmc.git.sourceforge.net/git/gitweb.cgi?p=xbmc/%s;a=tree;f=%s;hb=HEAD'

# Some helpful decorators
def escape(fn):
    '''A decorator that passes the returned value of the wrapped function to jinja2.escape()''' 
    def wrapped(*args, **kwargs):
        ret = fn(*args, **kwargs)
        return jinja2.escape(ret)
    return wrapped

def silence_attr_error(fn):
    '''A decorator to silence attribute errors when XML parsing. Catches the exception and returns None.'''
    def wrapped(*args, **kwargs):
        try:
            ret = fn(*args, **kwargs)
        except AttributeError:
            ret = None
        return ret
    return wrapped


class AddonXML(object):
    def __init__(self, path):
        self.path = path
        self.xmlstr = read(self.path)
        self.xml = BSS(self.xmlstr)

    @property
    def descriptions(self):
        '''A dictionary with language codes as keys and the corresponding descriptions as values.'''
        desc_tags = self.xml.findAll('description')

        # Get the 'lang' attribute as the key, and the actual description as the value
        desc = [(e(tag.get('lang', 'en')), e(tag.string)) for tag in desc_tags]
        return dict(desc)

    @property
    @silence_attr_error
    @escape
    def addon_id(self):
        return self.xml.find('addon').get('id')

    @property
    @silence_attr_error
    @escape
    def name(self):
        return self.xml.find('addon').get('name')

    @property
    @silence_attr_error
    @escape
    def version(self):
        return self.xml.find('addon').get('version')

    @property
    @silence_attr_error
    @escape
    def provider_name(self):
        return self.xml.find('addon').get('provider-name')

    @property
    @silence_attr_error
    @escape
    def platform(self):
        return self.xml.find('platform').string

    @property
    @silence_attr_error
    @escape
    def summary(self):
        return self.xml.find('summary').string

    @property
    @silence_attr_error
    @escape
    def disclaimer(self):
        return self.xml.find('disclaimer').string

    @property
    def addon_type(self):
        addon_id = self.addon_id or ''
        parts = addon_id.split('.')

        if parts[0] == 'plugin':
            # Matches plugin.(video|image|program|audio)
            return parts[1]
        elif parts[0] in ['script', 'skin', 'webinterface']:
            return parts[0]
        elif parts[0] == 'metadata':
            return 'scraper'
        else:
            return 'unknown'


class Addon(object):
    def __init__(self, repo, path):
        self.id = os.path.basename(path)
        self.path = path
        self.addonxml_path = self.path_or_none('addon.xml')
        #self.addonxml = AddonXML(self.addonxml_path)

        if self.addonxml_path:
            self.addonxml = AddonXML(self.addonxml_path)
        else:
            #self.addonxml = AddonXML()
            self.addonxml = None


        self.changelog= self.path_or_none('changelog.txt')

        #icon stuff
        icon_fn = self.path_or_none('icon.png')
        self._icon = None
        if icon_fn:
            self._icon = Image(icon_fn, self.id)

        self._fanart = self.path_or_none('fanart.jpg')
        self.repo = repo
        self.set_last_updated()

    def path_or_none(self, relpath):
        p = self.child_path(relpath)
        if os.path.isfile(p):
            return p
        return None

    def child_path(self, relpath):
        '''Returns an absolute child path from a given relative path.'''
        return os.path.join(self.path, relpath)

    def set_last_updated(self):
        '''Parses the last updated date from the git repo log.'''
        lines = self.repo.pretty_log()

        # Typically the commit msgs in the git log look like:
        #     [plugin.id] Some message here
        #
        # So we filter lines that contain the plugin name.
        commits = filter(lambda line: self.id in line, lines)

        if len(commits) == 0:
           print 'Couldn\'t deduce last updated date for %s.' % self.id 
           self._last_updated_timestamp = 0
        else:
            # We have a match in the log, so grab the most recent commit and parse the timestamp
            recent_commit = commits[0]
            timestamp, _ = recent_commit.split(' ', 1)
            self._last_updated_timestamp = timestamp

    def make_provider_html(self, name_string):
        tokens = name_string.split()
        # Strip some characters even though they are legal for forum names. Sometimes people
        # will write 'John Smith (jsmith)' 
        tokens = [token.strip('()[],') for token in tokens]
        urls = map(get_member_url, tokens)

        # Add links for matched tokens
        for token, url in zip(tokens, urls):
            #print 'token', token, type(token), url
            if url:
                html = jinja2.Markup('<a href="%s">%s</a>')
                url = jinja2.Markup(url)
                #name_string = name_string.replace(token, jinja2.Markup('<a href="%s">%s</a>' % (url, token)))
                name_string = name_string.replace(token, html % (url, token))
        #return name_string
        return name_string

    # Addon properties
    #@property
    #def changelog(self):
        #return read(self.changelog)

    @property
    def icon(self):
        return self._icon
        #return self.path_or_none('icon.png')

    @property
    def fanart(self):
        return self.path_or_none('fanart.jpg')

    @property
    def last_updated_human(self):
        return human_datetime(self._last_updated_timestamp)

    @property
    def last_updated_ts(self):
        return self._last_updated_timestamp

    @property
    def last_updated_iso(self):
        return '%sZ' % datetime.fromtimestamp(int(self._last_updated_timestamp)).isoformat()

    @property
    def provider_html(self):
        return self.make_provider_html(self.provider_name)

    @property
    def addon_id_html(self):
        if not self.addon_id:
            return self.addon_id
        gitweb_url = GITWEB_URL_PATTERN % (os.path.basename(self.repo.path.rstrip('/')), self.addon_id)
        return '<a href="%s">%s</a>' % (gitweb_url, self.addon_id)

    # AddonXML properties
    @property
    def descriptions(self):
        if self.addonxml:
            return self.addonxml.descriptions
        return {}

    @property
    @silence_attr_error
    def addon_id(self):
        return self.addonxml.addon_id

    @property
    @silence_attr_error
    def name(self):
        return self.addonxml.name

    @property
    @silence_attr_error
    def version(self):
        return self.addonxml.version

    @property
    @silence_attr_error
    def provider_name(self):
        return self.addonxml.provider_name

    @property
    @silence_attr_error
    def platform(self):
        return self.addonxml.platform

    @property
    @silence_attr_error
    def summary(self):
        return self.addonxml.summary

    @property
    @silence_attr_error
    def disclaimer(self):
        return self.addonxml.disclaimer

    @property
    @silence_attr_error
    def addon_type(self):
        return self.addonxml.addon_type

