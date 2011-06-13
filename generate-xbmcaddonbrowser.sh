#!/bin/bash

# virtualenv
export WORKON_HOME=$HOME/.virtualenvs
source virtualenvwrapper.sh
workon xbmcaddonbrowser
/home/jon/Repositories/xbmc-addon-browser/generator.py >> /var/log/xbmcaddonbrowser.com/generator.log

