from __future__ import absolute_import
from __future__ import print_function

import six

from . import defs

def _populate_options(opts):
    assert isinstance(opts, dict)
    opts = dict((k.upper(), v) for k,v in opts.iteritems() 
                if isinstance(k, six.string_types))
    newopts = defs.DEFAULT_OPTIONS.copy()
    newopts.update(opts)
    return newopts


class Options(object):
    def __init__(self, opts=None):
        opts = opts or {}
        self.opts = _populate_options(opts)
        
    def __getitem__(self, name):
        return self.opts[name.upper()]
        
    def __getattr__(self, name):
        try:
            return self.opts[name.upper()]
        except KeyError:
            msg = "'{}' object has no attribute '{}'"
            raise AttributeError(msg.format(type(self).__name__, name))
            
    def get(self, name, default=None):
        return self.opts.get(name.upper(), default)


