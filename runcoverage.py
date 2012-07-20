import os.path
from coverage import coverage
import cssypy.runtests

HTMLDIR = 'htmlcov'
SOURCE = ['cssypy']
INCLUDE = []
CONFIG = True
OMIT = ['cssypy/tests/*','cssypy/runtests.py',]


def main():
    cov = coverage(cover_pylib=False, branch=True, config_file=CONFIG, source=SOURCE, include=INCLUDE, omit=OMIT)
    cov.start()
    cssypy.runtests.main()
    cov.stop()
    cov.html_report(directory=HTMLDIR)

main()

