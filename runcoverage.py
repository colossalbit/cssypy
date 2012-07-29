#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function

import os.path
from coverage import coverage

HTMLDIR = 'htmlcov'
SOURCE = ['cssypy']
INCLUDE = []
CONFIG = True
OMIT = ['cssypy/tests/*','cssypy/runtests.py',]


def main():
    cov = coverage(cover_pylib=False, branch=True, config_file=CONFIG, source=SOURCE, include=INCLUDE, omit=OMIT)
    cov.start()
    import cssypy.runtests
    cssypy.runtests.main()
    cov.stop()
    cov.html_report(directory=HTMLDIR)

main()

