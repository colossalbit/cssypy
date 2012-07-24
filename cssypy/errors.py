from __future__ import absolute_import
from __future__ import print_function

class CSSError(Exception):
    pass


class CSSSyntaxError(CSSError):
    def __init__(self, msg, filename='', lineno=0, column=0, token=None):
        super(CSSSyntaxError, self).__init__(msg, filename, lineno, column)
        self.msg = msg
        self.filename = filename
        self.lineno = lineno
        self.column = column
        self.token = token
        
    def format_message(self, show_token=True):
        if self.filename and self.lineno:
            if self.column:
                fmt = '{msg} ({fname}, line {lno}, col {col})'
            else:
                fmt = '{msg} ({fname}, line {lno})'
        elif self.filename:
            fmt = '{msg} ({fname})'
        elif self.lineno:
            if self.column:
                fmt = '{msg} (line {lno}, col {col})'
            else:
                fmt = '{msg} (line {lno})'
        else:
            fmt = '{msg}'
        type = ''
        val = ''
        if show_token and self.token:
            type = self.token.typestr
            val = self.token.value
            fmt += ' (token {type}: {val!r})'
        return fmt.format(msg=self.msg, fname=self.filename, lno=self.lineno, 
                          col=self.column, type=type, val=val)
        
    def __str__(self):
        try:
            return self.format_message(show_token=True)
        except:
            import traceback
            traceback.print_exc()
            raise
            
            
class CSSImportError(CSSError):
    pass
    
class CSSImportNotFound(CSSImportError):
    pass
    
class CSSCircularImportError(CSSImportError):
    pass
    
class CSSEncodingNotFound(CSSError):
    pass
    
class CSSTypeError(CSSError):
    pass
    
class CSSVarNameError(CSSError):
    pass

