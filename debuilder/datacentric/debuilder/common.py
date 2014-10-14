import os

#working directory
BUILD_DIR  = "build"
#debian repository (used only in 'pub' command)
REPOSITORY = os.getenv('DEBREPOSITORY')
#where to put python modules
PYTHONPATH = "/usr/lib/python2.7/dist-packages/"

MODULE_DIR = os.path.dirname(__file__)
TEMPLATES_DIR = os.path.join(MODULE_DIR, 'templates')
