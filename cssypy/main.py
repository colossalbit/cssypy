from __future__ import absolute_import
from __future__ import print_function

import pprint

from .utils import useroptions, reporters
from . import defs, core, optionsdict

def get_optspec():
    optspec = useroptions.OptionSpec(usage='%(prog)s [options] INPUT OUTPUT')
    Opt = useroptions.OptionDef
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
        Opt('enable_imports',  type=bool, dest='ENABLE_IMPORTS', 
            metavar='(yes|no)', default=defs.ENABLE_IMPORTS,
            help='(default: yes)'))

    # enable/disable flatten
    optspec.add_optdef(
        Opt('enable_flatten',  type=bool, dest='ENABLE_FLATTEN', 
            metavar='(yes|no)', default=defs.ENABLE_FLATTEN,
            help='(default: yes)'))

    # enable/disable solve
    optspec.add_optdef(
        Opt('enable_solve',  type=bool, dest='ENABLE_SOLVE', 
            metavar='(yes|no)', default=defs.ENABLE_SOLVE,
            help='(default: yes)'))
    
    
    # enable/disable imports relative to the current stylesheet
    optspec.add_optdef(
        Opt('curfile_relative_imports',  type=bool, metavar='(enable|disable)', 
            dest='IMPORT_RELATIVE_TO_CURRENT_FILE', 
            default=defs.IMPORT_RELATIVE_TO_CURRENT_FILE,
            help='(default: enable)'))
    
    # enable/disable imports relative to the top-level stylesheet
    optspec.add_optdef(
        Opt('toplevel_relative_imports',  type=bool, metavar='(enable|disable)', 
            dest='IMPORT_RELATIVE_TO_TOPLEVEL_STYLESHEET', 
            default=defs.IMPORT_RELATIVE_TO_TOPLEVEL_STYLESHEET,
            help='(default: enable)'))
    
    return optspec
    
def _main(cmdline=None, reporter=None):
    reporter = reporter or reporters.NullReporter()
    
    optspec = get_optspec()
    optsreader = useroptions.OptionsReader(optspec, reporter)
    optdict = optsreader.get_options(cmdline=cmdline)
    
    ifile = optdict.pop('input')
    ofile = optdict.pop('output')
    default_encoding = optdict.pop('default_encoding', None)
    source_encoding = optdict.pop('source_encoding', None)
    dest_encoding = optdict.pop('dest_encoding', None)
    import_directories = []  # TODO
    
    options = optionsdict.Options(optdict)
    
    core.compile(ifile, ofile, 
                 source_encoding=source_encoding, 
                 dest_encoding=dest_encoding, 
                 default_encoding=default_encoding, 
                 import_directories=import_directories, 
                 options=options, 
                 reporter=reporter)

def main():     # pragma: no cover
    reporter = reporters.Reporter()
    try:
        _main(reporter=reporter)
    except SystemExit as e:
        pass
    #except Exception as e:
    #    reporter.critical('Unhandled exception.')



