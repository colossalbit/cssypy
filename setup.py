import os.path

from setuptools import setup, find_packages

import cssypy

THISDIR = os.path.abspath(os.path.dirname(__file__))

def read_requirements(fname):
    fpath = os.path.join(THISDIR, fname)
    with open(fpath, 'r') as f:
        reqs = []
        for line in f:
            i = line.find('#')
            if i != -1:
                line = line[:i]
            if line.strip():
                reqs.append(line.strip())
    return reqs

install_requires = read_requirements('requirements.pip')
import pprint
pprint.pprint(install_requires)

setup(
    name = 'CSSyPy',
    version = cssypy.__version__,
    packages = find_packages(),
    include_package_data = True,
    
    install_requires = install_requires,
    zip_safe = False,
    
    author = 'David White',
    author_email = 'TODO',
    description = 'TODO',
    license='BSD',
    keywords = 'css',
    url = 'TODO',
)