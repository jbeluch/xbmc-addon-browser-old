import os

cwd = os.path.dirname(__file__)

CONTENT_PATH = os.path.join(cwd, 'content')
MEDIA_PATH = os.path.join(cwd, 'media')
JS_PATH = os.path.join(MEDIA_PATH, 'js')
CSS_PATH = os.path.join(MEDIA_PATH, 'css')
IMG_PATH = os.path.join(MEDIA_PATH, 'img')
BUILD_PATH = os.path.join(cwd, 'build')
TEMPLATES_PATH = os.path.join(cwd, 'templates')
BUILD_INFO = os.path.join(cwd, '.build_info')
DEPLOY_DIR = os.path.join(cwd, 'deploy')

# Path to git repos for plugins. all of these will be combind into a single page
REPOS = [
    '/home/jon/Repositories/xbmc/plugins/',
    '/home/jon/Repositories/xbmc/scripts/',
    '/home/jon/Repositories/xbmc/scrapers/',
    '/home/jon/Repositories/xbmc/skins/',
    '/home/jon/Repositories/xbmc/webinterfaces/',
    '/home/jon/Repositories/xbmc/visualizations/',
    '/home/jon/Repositories/xbmc/screensavers/',
]
