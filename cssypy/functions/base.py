import inspect
import collections
import types

from .. import errors

FuncEntry = collections.namedtuple('FuncEntry', 'name func nargs')


class FunctionRegistry(object):
    def __init__(self):
        self.funcs = {}
        
    def register(self, func, name=None, nargs=None):
        argspec = inspect.getargspec(func)
        name = name or func.__name__
        nargs = nargs if nargs is not None else len(argspec.args)
        if name not in self.funcs:
            self.funcs[name] = {}
        self.funcs[name][nargs] = FuncEntry(name, func, nargs)
        
    def getfunc(self, name, nargs):
        try:
            nfunc = self.funcs[name]
            try:
                return nfunc[nargs].func
            except KeyError:
                raise errors.CSSFunctionNotFound()
        except KeyError:
            raise errors.CSSFunctionNotFound()
        
        
registry = FunctionRegistry()
builtin_registry = FunctionRegistry()

def register(*args, **kwargs):
    if not kwargs and len(args) == 1 and callable(args[0]):
        registry.register(args[0])
        return args[0]
    else:
        def inner(func):
            registry.register(func, *args, **kwargs)
            return func
        return inner
        
        
def register_builtin(*args, **kwargs):
    if not kwargs and len(args) == 1 and callable(args[0]):
        builtin_registry.register(args[0])
        return args[0]
    else:
        def inner(func):
            builtin_registry.register(func, *args, **kwargs)
            return func
        return inner
    
def get_function(name, nargs):
    try:
        func = builtin_registry.getfunc(name, nargs)
    except errors.CSSFunctionNotFound:
        func = registry.getfunc(name, nargs)
    return func
    
def call(name, args):
    func = get_function(name, len(args))
    return func(*args)

