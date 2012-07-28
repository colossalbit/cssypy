import os.path

from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

THISDIR = os.path.abspath(os.path.dirname(__file__))

def read_init_module():
    # cssypy/__init__.py does not have any imports, so just run it as a script 
    # to get its version information.
    filename = os.path.join(THISDIR, 'cssypy', '__init__.py')
    print('filename: {0}'.format(filename))
    with open(filename, 'r') as f:
        src = f.read()
    # use compile() and eval() because they work in both Python 2 and 3.
    code = compile(src, filename, 'exec')
    globals = locals = {}
    eval(code, globals, locals)
    return globals

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

meta = read_init_module()
install_requires = read_requirements('requirements.pip')

classifiers = """
    Development Status :: 3 - Alpha
    Environment :: Console
    Environment :: Web Environment
    Intended Audience :: Developers
    Intended Audience :: Information Technology
    License :: OSI Approved :: BSD License
    Operating System :: OS Independent
    Programming Language :: Python
    Programming Language :: Python :: 2.7
    Topic :: Internet
    Topic :: Internet :: WWW/HTTP
    Topic :: Text Processing
"""
classifiers = [line.strip() for line in classifiers.splitlines() if line.strip()]

setup(
    name = 'CSSyPy',
    version = meta['__version__'],
    description = meta['__doc__'],
    author = 'David White',
    author_email = 'colossalbit@gmail.com',
    url = 'https://github.com/colossalbit/cssypy',
    keywords = ['css', 'css processor'],
    classifiers = classifiers,
    license = 'BSD',
    platforms = ['any'],
    #long_description = ???,
    
    packages = find_packages(),
    include_package_data = True,
    install_requires = install_requires,
    zip_safe = True,
    
    test_suite = 'cssypy.tests',
)
