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

from urllib import urlopen, urlencode
from urlparse import urljoin
from BeautifulSoup import BeautifulSoup as BS
from utils import read_lines
import re
import os

BASE_URL = 'http://forum.xbmc.org'
MEMBER_SEARCH_URL = '%s/memberlist.php?do=getall' % BASE_URL

def download_page(url, body=None):
    u = urlopen(url, body)
    src = u.read()
    u.close()
    return src

def load_cache(fn):
    lines = read_lines(fn)

    pairs = [line.strip().split() for line in lines]
    pairs = filter(lambda pair: len(pair) == 2, pairs)
    cache = dict(pairs)

    # Update cache with actual None values instead of the string 'None'
    for k, v in cache.items():
        if v == 'None':
            cache[k] = None
    return cache

def append_to_cache(fn, name, url):
    with open(fn, 'a') as f:
        f.write('%s %s\n' % (name.encode('utf-8'), url))

def get_member_url(name, cache_fn=None):
    print 'Attempting to find forum.xbmc.org profile for %s.' % name
    # eventually set expirations for the cache
    # hardcode cache fn for now
    if not cache_fn:
        cache_fn = os.path.join(os.path.dirname(__file__), 'cache', 'xbmcforum_users')

    cache = load_cache(cache_fn)

    if name in cache.keys():
        return cache[name]

    args = {
        's': '',
        'securitytoken': 'guest',
        'do': 'getall',
        #'ausername': name.encode('utf-8'),
        'ausername': name.encode('utf-8'),
    }

    html = BS(download_page(MEMBER_SEARCH_URL, urlencode(args)))
    a_tags = html.findAll('a', {'href': re.compile('^member.php*')})

    # Now filter by exact name match only
    # Can't include texdt search in html.find because it retuns String objects not tags
    matches = filter(lambda tag: tag.find(text=True).lower() == name.lower(), a_tags)

    if len(matches) == 1:
        url = urljoin(BASE_URL, matches[0]['href'])
        append_to_cache(cache_fn, name, url)
        return url
    else:
        # No exact match
        append_to_cache(cache_fn, name, 'None')
        return None
    


if __name__ == '__main__':
    print get_member_url('twinther')
    print get_member_url('divingmule')
