from __future__ import absolute_import
from __future__ import print_function

DEFAULT_ENCODING = 'utf_8'

CONFIG_FILENAME = 'cssypy.conf'
CONFIGFILE_OPTNAME = 'conf'

STDIN =  -1
STDOUT = -2
STDERR = -3

DEFAULT_OPTIONS = {
    'ENABLE_FLATTEN': True,
    'ENABLE_SOLVE': True,
    'ENABLE_IMPORTS': True,
    
    'IMPORT_RELATIVE_TO_CURRENT_FILE': True,
    'IMPORT_RELATIVE_TO_TOPLEVEL_STYLESHEET': True,
    'STOP_ON_IMPORT_NOT_FOUND': False,
    'STOP_ON_IMPORT_SYNTAX_ERROR': True,
    
    'PROPAGATE_EXCEPTIONS': False,
    
    'IMPORT_FINDERS': (),
}


for k,v in DEFAULT_OPTIONS.iteritems():
    globals()[k] = v

