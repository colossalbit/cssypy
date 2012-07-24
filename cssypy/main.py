from __future__ import absolute_import
from __future__ import print_function

import pprint

from .utils import options, reporters
from . import defs, core

def get_optspec():
    optspec = options.OptionSpec(usage='%(prog)s [options] INPUT OUTPUT')
    Opt = options.OptionDef
    optspec.add_optdef(
        Opt('input',  metavar='INPUT',  file_option=False, is_argument=True, 
            help='The input stylesheet. Use - to read from stdin.'))
    optspec.add_optdef(
        Opt('output', metavar='OUTPUT', file_option=False, is_argument=True,
            help='The stylesheet to write to. Use - to write to stdout.'))
    optspec.add_optdef(
        Opt(defs.CONFIGFILE_OPTNAME, file_option=False, 
            help='Config file. (default: {})'.format(defs.CONFIG_FILENAME)))
    
    optspec.add_optdef(Opt('default_encoding', metavar='ENCODING'))
    optspec.add_optdef(Opt('source_encoding',  metavar='ENCODING'))
    optspec.add_optdef(Opt('dest_encoding',    metavar='ENCODING'))
    
    # enable/disable imports
    optspec.add_optdef(
        Opt('enable_imports',  type=bool, dest='enable_imports', 
            metavar='(yes|no)', default=defs.ENABLE_IMPORTS,
            help='(default: yes)'))
    # optspec.add_optdef(
        # Opt('enable_imports',  type=bool, action='store_true', 
            # dest='enable_imports', default=defs.ENABLE_IMPORTS))
    # optspec.add_optdef(
        # Opt('disable_imports', type=bool, action='store_false', 
            # dest='enable_imports', cmdline_helper=True))

    # enable/disable flatten
    optspec.add_optdef(
        Opt('enable_flatten',  type=bool, dest='enable_flatten', 
            metavar='(yes|no)', default=defs.ENABLE_FLATTEN,
            help='(default: yes)'))
    # optspec.add_optdef(
        # Opt('enable_flatten',  type=bool, action='store_true',  
            # dest='enable_flatten', default=defs.ENABLE_FLATTEN))
    # optspec.add_optdef(
        # Opt('disable_flatten', type=bool, action='store_false', 
            # dest='enable_flatten', cmdline_helper=True))

    # enable/disable solve
    optspec.add_optdef(
        Opt('enable_solve',  type=bool, dest='enable_solve', 
            metavar='(yes|no)', default=defs.ENABLE_SOLVE,
            help='(default: yes)'))
    # optspec.add_optdef(
        # Opt('enable_solve',  type=bool, action='store_true',  
            # dest='enable_solve', default=defs.ENABLE_SOLVE))
    # optspec.add_optdef(
        # Opt('disable_solve', type=bool, action='store_false', 
            # dest='enable_solve', cmdline_helper=True))
    
    
    # enable/disable imports relative to the current stylesheet
    optspec.add_optdef(
        Opt('curfile_relative_imports',  type=bool, metavar='(enable|disable)', 
            dest='curfile_relative_imports', 
            default=defs.IMPORT_RELATIVE_TO_CURRENT_FILE,
            help='(default: enable)'))
            
    # optspec.add_optdef(
        # Opt('enable_curfile_relative_imports',  type=bool, action='store_true', 
            # dest='curfile_relative_imports', 
            # default=defs.IMPORT_RELATIVE_TO_CURRENT_FILE))
    # optspec.add_optdef(
        # Opt('disable_curfile_relative_imports', type=bool, action='store_false', 
            # dest='curfile_relative_imports', cmdline_helper=True))
    
    # enable/disable imports relative to the top-level stylesheet
    optspec.add_optdef(
        Opt('toplevel_relative_imports',  type=bool, metavar='(enable|disable)', 
            dest='toplevel_relative_imports', 
            default=defs.IMPORT_RELATIVE_TO_TOPLEVEL_STYLESHEET,
            help='(default: enable)'))
    # optspec.add_optdef(
        # Opt('enable_toplevel_relative_imports',  type=bool, action='store_true',
            # dest='toplevel_relative_imports', 
            # default=defs.IMPORT_RELATIVE_TO_TOPLEVEL_STYLESHEET))
    # optspec.add_optdef(
        # Opt('disable_toplevel_relative_imports', type=bool, 
            # action='store_false', dest='toplevel_relative_imports', 
            # cmdline_helper=True))
    
    return optspec
    
def _main(cmdline=None, reporter=None):
    reporter = reporter or reporters.NullReporter()
    
    optspec = get_optspec()
    optsreader = options.OptionsReader(optspec, reporter)
    optdict = optsreader.get_options(cmdline=cmdline)
    
    ifile = optdict.pop('input')
    ofile = optdict.pop('output')
    default_encoding = optdict.pop('default_encoding', None)
    source_encoding = optdict.pop('source_encoding', None)
    dest_encoding = optdict.pop('dest_encoding', None)
    import_directories = []  # TODO
    
    core.compile(ifile, ofile, 
                 source_encoding=source_encoding, 
                 dest_encoding=dest_encoding, 
                 default_encoding=default_encoding, 
                 import_directories=import_directories, 
                 options=optdict, 
                 reporter=reporter)

def main():
    reporter = reporters.Reporter()
    try:
        _main(reporter=reporter)
    except SystemExit as e:
        pass
    #except Exception as e:
    #    reporter.critical('Unhandled exception.')



