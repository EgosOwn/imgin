from gevent import monkey
from gevent import sleep
monkey.patch_all()
from threading import Thread
from os import remove, mkdir, path, stat
from shutil import rmtree

from uuid import uuid4

from bottle import route, run
from bottle import static_file
from bottle import SimpleTemplate

from .get import get
from .config import IMAGE_CACHE, template_dir


def get_timestamp_of_file(file):
    return stat(file).st_ctime

def album(id):
    req = IMAGE_CACHE

    get("/a/" + id, req)
    found_list_file = IMAGE_CACHE + ("/a/" + id).replace('/', '_')

    with open(found_list_file, 'r') as f:
        imgs = f.read().split(',')

    for c, img in enumerate(imgs):
        imgs[c] = IMAGE_CACHE + imgs[c]

    # sort image order (file creation time)
    imgs = sorted(imgs, key=get_timestamp_of_file)

    for c, img in enumerate(imgs):
        imgs[c] = img.replace(IMAGE_CACHE, '/')



    with open(f'{template_dir}gallery.html', 'r') as img_view:
        tpl = SimpleTemplate(img_view)
    return tpl.render(imgs=imgs)

@route('/')
@route('')
def home():
    return static_file("index.html", root=template_dir)

@route('/static/<file>')
def static(file=''):
    return static_file(file, root=template_dir)


@route('/gallery/<id>')
def gallery(id=''):
    return album(id)

@route('/a/<id>')
def gallery(id=''):
    return album(id)


@route('/<img>')
def img(img=''):
    if not img.endswith("jpeg") and not img.endswith("jpg") and not img.endswith("png"):
        img = img + ".jpg"
    img = img.replace('jpeg', 'jpg')
    if not path.exists(IMAGE_CACHE + img):
        get(img, IMAGE_CACHE)
    return static_file(img, root=IMAGE_CACHE)


def start_server():
    try:
        rmtree(IMAGE_CACHE)
    except FileNotFoundError:
        pass
    mkdir(IMAGE_CACHE)

    run(server='gevent', host='0.0.0.0')