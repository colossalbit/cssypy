#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function

import os.path
import shutil

from coverage import coverage

HTMLDIR = 'htmlcov'
CURPATH = os.path.abspath(os.path.dirname(__file__))
HTMLPATH = os.path.join(CURPATH, HTMLDIR)

SOURCE = ['cssypy']
INCLUDE = []
CONFIG = True
OMIT = ['cssypy/tests/*','cssypy/runtests.py',]


def main():
    for name in os.listdir(HTMLPATH):
        os.remove(os.path.join(HTMLPATH, name))
        
    cov = coverage(cover_pylib=False, branch=True, config_file=CONFIG, source=SOURCE, include=INCLUDE, omit=OMIT)
    cov.start()
    import cssypy.runtests
    cssypy.runtests.main()
    cov.stop()
    cov.html_report(directory=HTMLPATH)

main()

