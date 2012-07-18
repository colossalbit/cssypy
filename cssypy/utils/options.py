import os.path
import argparse
import ConfigParser as configparser
import collections
import __builtin__

from . import reporters
from .. import defs

#==============================================================================#
_true_strings =  set('true  t yes y 1 on  enable'.split())
_false_strings = set('false f no  n 0 off disable'.split())

def string_bool(val):
    val = val.lower()
    if val in _true_strings:
        return True
    elif val in _false_strings:
        return False
    else:
        raise ValueError('String is not a known boolean value.')


#==============================================================================#
class OptionDef(object):
    def __init__(self, name, argnames=None, default=None, type=None, 
                 choices=None, help=None, argparser_kwargs=None, 
                 cmdline_option=True, file_option=True, list=False, 
                 is_argument=False, metavar=None, dest=None, action=None, 
                 cmdline_helper=False, hide=False):
        assert '-' not in name
        self.name = name    # name used to store the option
        assert argnames is None or isinstance(argnames, tuple)
        self._argnames = argnames
        if list:
            self.default = default or __builtin__.list
        else:
            self.default = default
        self.type = type or unicode
        self.choices = choices
        self.help = help    # used only by argparser
        self.list = list
        self._argparser_kwargs = argparser_kwargs or {}
        self.metavar = metavar
        self.dest = dest
        self.action = action
        if cmdline_helper:
            self.cmdline_option = True
            self.file_option = False
            self.hide = True
        else:
            self.cmdline_option = True if is_argument else cmdline_option
            self.file_option = False if is_argument else file_option
            self.hide = hide
        self.is_argument = is_argument
        
    def argparser_names(self):
        if self._argnames:
            return self._argnames
        elif self.is_argument:
            return (self.name.replace('_', '-'),)
        else:
            return ('--'+self.name.replace('_', '-'),)
        
    def configfile_name(self):
        return self.name.lower()
        
    def _conv_elem(self, x):
        x = self.configfile_type()(x)
        if self.choices and x not in self.choices:
            raise RuntimeError()
        return x
        
    def configfile_conv(self, x):
        if self.list:
            return [self._conv_elem(x.strip()) for x in x.split(',')]
        else:
            return self._conv_elem(x.strip())
            
    def configfile_type(self):
        if self.type == bool:
            return string_bool
        return self.type
            
    def argparser_type(self):
        if self.type == bool:
            return string_bool
        return self.type
        
    def get_default(self):
        if isinstance(self.default, collections.Callable):
            return self.default()
        return self.default
        
    def argparser_kwargs(self):
        kwargs = self._argparser_kwargs.copy()
        # Do not use defaults on command line so they can be overridden by 
        # config file.
        kwargs['default'] = argparse.SUPPRESS
        if self.action not in ('store_true', 'store_false'):
            kwargs['type'] = self.argparser_type()
        if not self.is_argument:
            if self.dest:
                kwargs['dest'] = self.dest
            else:
                kwargs['dest'] = self.name
        if self.help:
            kwargs['help'] = self.help
        if self.choices:
            kwargs['choices'] = self.choices
        if self.metavar:
            kwargs['metavar'] = self.metavar
        if self.action:
            kwargs['action'] = self.action
        if self.list:
            kwargs['nargs'] = '*'
        return kwargs
    
    
#==============================================================================#
class OptGroupDef(object):
    def __init__(self, name, description=None):
        self.name = name
        self.description = description
        self.optdefs = []
        self.optnames = set()

    def add_optdef(self, optdef):
        assert optdef.name.lower() not in self.optnames
        self.optdefs.append(optdef)
        self.optnames.add(optdef.name.lower())
        
    def iteroptions(self):
        return (opt for opt in self.optdefs if not opt.hide)
        
    def iter_cmdline_options(self):
        return (opt for opt in self.optdefs if opt.cmdline_option)
        
    def iter_file_options(self):
        return (opt for opt in self.optdefs if opt.file_option)


#==============================================================================#
class OptionSpec(object):
    def __init__(self, default_name='General', default_description=None,
                 usage=None, prog=None, description=None, epilog=None):
        self.usage = usage
        self.prog = prog
        self.description = description
        self.epilog = epilog
        
        self.optdefs = []
        self.groupdefs = []
        self.optnames = set()    # test for duplicates
        self.groupnames = set()  # test for duplicates
        
        self._default_group = OptGroupDef(default_name, default_description)
        self.add_groupdef(self._default_group)
        
    def argparser_kwargs(self):
        kwargs = {}
        if self.usage:
            kwargs['usage'] = self.usage
        if self.prog:
            kwargs['prog'] = self.prog
        if self.description:
            kwargs['description'] = self.description
        if self.epilog:
            kwargs['epilog'] = self.epilog
        return kwargs

    def add_optdef(self, optdef):
        assert optdef.name.lower() not in self.optnames
        self._default_group.add_optdef(optdef)
        self.optnames.add(optdef.name.lower())
        
    def add_groupdef(self, groupdef):
        assert groupdef.name.lower() not in self.groupnames
        for opt in groupdef.iteroptions():
            assert opt.name.lower() not in self.optnames
            self.optnames.add(opt.name.lower())
        self.groupdefs.append(groupdef)
        self.groupnames.add(groupdef.name.lower())
        
    def get_groupdef(self, name):
        lname = name.lower()
        for group in self.groupdefs:
            if group.name.lower() == lname:
                return group
        raise KeyError("OptionSpec has no OptGroupDef '{}'.".format(name))
        
    def itergroups(self, include_default_group=True):
        if include_default_group:
            return iter(self.groupdefs)
        else:
            return iter(self.groupdefs[1:])
        
    def iteroptions(self):
        return self.groupdefs[0].iteroptions()
        
    def _iteroptions(self):
        return iter(self.groupdefs[0].optdefs)
        
    def iter_cmdline_options(self):
        return (opt for opt in self._iteroptions() if opt.cmdline_option)
        
    def iter_file_options(self):
        return (opt for opt in self._iteroptions() if opt.file_option)
        

#==============================================================================#
class OptionsReader(object):
    def __init__(self, optspec, reporter=None):
        self.reporter = reporter or reporters.NullReporter()
        self.optspec = optspec
        self.config_filename = None
    
    def build_argparser(self, argparser):
        # general options
        for opt in self.optspec.iter_cmdline_options():
            argparser.add_argument(*opt.argparser_names(), 
                                   **opt.argparser_kwargs())
        # group options
        for groupdef in self.optspec.itergroups(include_default_group=False):
            arggroup = argparser.add_argument_group(groupdef.name, 
                                                    groupdef.description)
            for opt in groupdef.iter_cmdline_options():
                arggroup.add_argument(*opt.argparser_names(), 
                                      **opt.argparser_kwargs())
        return argparser

    def get_argparser(self):
        parser = argparse.ArgumentParser(**self.optspec.argparser_kwargs())
        parser = self.build_argparser(parser)
        return parser
        
    def find_config_file(self, filename):
        # if filename has no path, try in common locations
        # if filename has path, try in common locations?
        # return None if file not found, otherwise return filename
        homepath = os.path.expanduser('~')
        for dir in ('', homepath):
            filepath = os.path.join(dir, filename)
            if os.path.isfile(filepath):
                return filepath
        return None
        
    def parse_config_file(self, filename=None):
        # 1. Determine the file name.
        filename = filename or defs.CONFIG_FILENAME
        filepath = self.find_config_file(filename)
        if not filepath:
            m = "Config file '{0}' not found.".format(filename)
            self.reporter.warning(m)
            return {}
        
        # 2. Open and parse the file
        parser = configparser.ConfigParser()
        try:
            with open(filepath, 'r') as f:
                parser.readfp(f, filepath)
        except (IOError, OSError):
            m = "Error trying to open config file '{0}'.".format(filename)
            self.reporter.warning(m)
            return {}
        
        # 3. Read the contents into a dict.
        confdict = {}
        for groupdef in self.optspec.itergroups():
            section = groupdef.name
            for opt in groupdef.iter_file_options():
                try:
                    val = parser.get(section, opt.configfile_name(), raw=True)
                    # TODO: handle exception when configfile_conv() fails
                    val = opt.configfile_conv(val)
                    confdict[opt.name] = val
                except (configparser.NoSectionError, configparser.NoOptionError):
                    pass
        return confdict
        
    def get_cmdline_options(self, cmdline=None):
        argparser = self.get_argparser()
        args = argparser.parse_args(args=cmdline)
        argsdict = vars(args)
        self.config_filename = argsdict.get(defs.CONFIGFILE_OPTNAME, None) or None
        return argsdict
        
    def get_file_options(self, filename=None):
        confdict = self.parse_config_file(filename or self.config_filename)
        return confdict
        
    def merge_options(self, argsdict, confdict):
        for opt in self.optspec.iteroptions():
            if opt.name not in argsdict:
                if opt.name in confdict:
                    argsdict[opt.name] = confdict[opt.name]
                else:
                    argsdict[opt.name] = opt.get_default()
        return argsdict
        
    def get_options(self, cmdline=None, config_filename=None):
        argsdict = self.get_cmdline_options(cmdline)
        confdict = self.get_file_options(config_filename)
        optdict = self.merge_options(argsdict, confdict)
        return optdict


#==============================================================================#

