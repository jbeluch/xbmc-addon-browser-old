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
import Image

# python str.format() syntax, {{ is an escaped {
CSS_TPL = '''{selector} {{
    background-position: 0 {ypos}px;
}}
'''

COMMON_TPL = '''{selector} {{
    background-image: url('{path}');
}}
'''

class CSSSpriteSheet(object):
    def __init__(self, image_selector_paths):
        self.image_selector_paths = image_selector_paths
        self.selectors = [selector for selector, path in self.image_selector_paths]
        self.paths = [path for selector, path in self.image_selector_paths]
        self.images = [Image.open(path) for _, path in self.image_selector_paths]
        #self.images = map(Image.open, image_paths)
        self.sprite_sheet = self.make_spritesheet(self.images)
        #self.css = self.make_css(self.image_selector_paths, public_rel_path)
        self.css = self.make_css(self.selectors)

    def make_css(self, selectors):
        css = ''
        _, height = self.images[0].size

        ypos = 0
        for count, selector in enumerate(selectors):
            ypos = count * height
            css += CSS_TPL.format(selector=selector, ypos=ypos)

        return css

    def make_spritesheet(self, images):
        width, height = images[0].size
        owidth = width
        oheight = height * len(images)

        output = Image.new(
            mode='RGBA',
            size=(owidth, oheight),
            color=(0,0,0,0),  # fully transparent
        )

        # Paste each of the images into the output image
        for count, image in enumerate(images):
            location = height * count
            output.paste(image, (0, location))

        return output

    def save_png(self, ofn):
        '''Takes a full filename and saves the spritesheet'''
        self.sprite_sheet.save(ofn)

    def save_gif(self, ofn):
        '''Takes a full filename and saves the spritesheet'''
        self.sprite_sheet.save(ofn, transparency=0)

    def save_css(self, ofn, common_selector, sprite_sheet_path):
        with open(ofn, 'w') as f:
            f.write(COMMON_TPL.format(selector=common_selector, path=sprite_sheet_path))
            f.write(self.css)

#if __name__ == '__main__':
    #images = [
        #('#plugin.image.facebook', 'icon_plugin.image.facebook.png'),
        #('#plugin.image.flickr', 'icon_plugin.image.flickr.png'),
        #('#plugin.image.google', 'icon_plugin.image.google.png'),
        #('#plugin.image.icanhascheezburger.com', 'icon_plugin.image.icanhascheezburger.com.png'),
        #('#plugin.image.iphoto', 'icon_plugin.image.iphoto.png'),
        #('#plugin.image.lastfm', 'icon_plugin.image.lastfm.png'),
        #('#plugin.image.mypicsdb', 'icon_plugin.image.mypicsdb.png'),
        #('#plugin.image.picasa', 'icon_plugin.image.picasa.png'),
    #]

    #sprite = CSSSpriteSheet(images)
    #sprite.save_png('icons_all.png')
    #sprite.save_gif('icons_all.gif')
    #sprite.save_css('icons_all_png.css', 'li', 'icons_all.png')
    #sprite.save_css('icons_all_gif.css', 'li', 'icons_all.gif')

