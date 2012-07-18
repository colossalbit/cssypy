#
# Script for running cssypy tests.
#
# This can be invoked in several different ways.
# 1) Run as module (if it's in site-packages or otherwise on your Python path):
#
#       $ python -m cssypy.runtests
#
# 2) Run directly from within the cssypy package directory:
#
#       $ python runtests.py
#

import sys
import os.path
import unittest
import argparse

# Put cssypy on the python path...
CURPATH = os.path.dirname(os.path.abspath(__file__))
PARENTPATH = os.path.dirname(CURPATH)

if PARENTPATH not in sys.path:
    sys.path.insert(0, PARENTPATH)

# Get ready to run our tests...
STARTDIR = os.path.join(CURPATH, 'tests')
TOPLEVELDIR = PARENTPATH
PATTERN = 'test_*'

def get_cmdline_args(argv):
    parser = argparse.ArgumentParser(description='Run unit tests.')
    parser.add_argument('--verbosity', '-v', dest='verbosity', action='store', 
                        type=int, choices=(0,1,2), default=1)
    parser.add_argument('--label', '-l', dest='label', metavar='LABEL', default=None)
    return parser.parse_args(args=argv)
    
    
def is_package(label):
    parts = tuple(label.split('.'))
    path = os.path.join(PARENTPATH, *parts)
    if os.path.isdir(path) and os.path.isfile(os.path.join(path, '__init__.py')):
        return True
    return False
    
    
def build_suite(label):
    loader = unittest.defaultTestLoader
    
    # No label was given; run all tests.
    if not label:
        print('Running all tests...\n')
        return loader.discover(STARTDIR, PATTERN, TOPLEVELDIR)
    
    label = 'cssypy.tests.' + label
    
    # Perhaps the label is a package; run the tests in it.
    if is_package(label):
    
        try:
            suite = loader.discover(label, PATTERN, TOPLEVELDIR)
            print('Running tests in package:\n{0}\n'.format(label))
            return suite
        except:
            # Oops, we couldn't run the test!
            print('ERROR: Unable to find test: {0}'.format(label))
    
    # Perhaps the label is a module, class, or method; run that.
    else:
        try:
            suite = loader.loadTestsFromName(label)
            print('Running tests in module/class/method:\n{0}\n'.format(label))
            return suite
        except:
            # Oops, we couldn't run the test!
            print('ERROR: Unable to find test: {0}'.format(label))
    return None
    

def main():
    args = get_cmdline_args(sys.argv[1:])
    test_suite = build_suite(args.label)
    if test_suite:
        unittest.TextTestRunner(verbosity=args.verbosity).run(test_suite)
        
if __name__ == '__main__':
    main()




