import os
from glob import glob
from flask import Markup

def get_slider_images():
    li = []
    for n in glob(os.path.join(os.path.dirname(__file__), "static", "images", "slider", "*")):
        li.append(os.path.split(n)[-1])
    return li

def del_slider_image(name):
    link = os.path.join(os.path.dirname(__file__), "static", "images", "slider", name)
    try:
        os.remove(link)
        return True
    except Exception:
        return False

