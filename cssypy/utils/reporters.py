from __future__ import absolute_import
from __future__ import print_function

import sys

STDERR = 1
STDOUT = 2

def _get_stream(x):
    if x is None:
        return None
    elif x == STDERR:
        return sys.stderr
    elif x == STDOUT:
        return sys.stdout
    else:
        return x
        
CRITICAL =  50
ERROR =     40
WARNING =   30
WARN =      WARNING
INFO =      20
DEBUG =     10
NOTSET =     0


class ReporterBase(object):
    def __init__(self, error_stream=STDERR, std_stream=STDOUT, level=INFO):
        self.error_stream = _get_stream(error_stream)
        self.std_stream = _get_stream(std_stream)
        self.level = level
        
    def critical(self, msg):
        if self.level <= CRITICAL and self.error_stream:
            self.error_stream.write(msg + '\n')
        
    def error(self, msg):
        if self.level <= ERROR and self.error_stream:
            self.error_stream.write(msg + '\n')
            
    def warning(self, msg):
        if self.level <= WARNING and self.error_stream:
            self.error_stream.write(msg + '\n')
        
    def info(self, msg):
        if self.level <= INFO and self.std_stream:
            self.std_stream.write(msg + '\n')
        
    def debug(self, msg):
        if self.level <= DEBUG and self.std_stream:
            self.std_stream.write(msg + '\n')


class Reporter(ReporterBase):
    def __init__(self, *args, **kwargs):
        super(Reporter, self).__init__(*args, **kwargs)
        
    def on_syntax_error(self, e):
        fmt = 'Syntax error:: {}'
        msg = fmt.format(e.format_message(show_token=False))
        self.error(msg)
        
        
class NullReporter(object):
    def critical(self, msg): pass
    def error(self, msg): pass
    def warning(self, msg): pass
    def info(self, msg): pass
    def debug(self, msg): pass


