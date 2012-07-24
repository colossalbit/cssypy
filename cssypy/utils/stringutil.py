from __future__ import absolute_import
from __future__ import print_function

import re
import codecs
import sys

from .py3compat import uchr, PYTHON3

UNESCAPE_IDENT = ur'\\(?P<ucs6>[0-9A-Fa-f]{6})|\\(?P<ucs>[0-9A-Fa-f]{1,5})(?:\r\n|[ \t\r\n\f])?|\\(?P<char>[^\r\nA-Fa-f0-9])'
ESCAPE_NMSTART = ur'(?P<digit>[0-9])|(?P<other>[^A-Za-z_\U000000A0-\U0010ffff\u00A0-\uffff])'     # lead character, cannot be a digit
ESCAPE_NMCHAR = ur'(?P<other>[^-A-Za-z0-9_\U000000A0-\U0010ffff\u00A0-\uffff])' # trailing character, may be a digit
UNESCAPE_STRING = UNESCAPE_IDENT + ur'|\\(?P<nl>\r\n|[\r\n])'
ESCAPE_DQUOTE_STRING = ur'[\\"]'
ESCAPE_SQUOTE_STRING = ur"[\\']"

re_unescape_ident = re.compile(UNESCAPE_IDENT)
re_escape_nmstart = re.compile(ESCAPE_NMSTART, re.UNICODE)
re_escape_nmchar =  re.compile(ESCAPE_NMCHAR, re.UNICODE)
re_unescape_string = re.compile(UNESCAPE_STRING)
re_escape_dquote_string = re.compile(ESCAPE_DQUOTE_STRING, re.UNICODE)
re_escape_squote_string = re.compile(ESCAPE_SQUOTE_STRING, re.UNICODE)

#==============================================================================#
if PYTHON3: # pragma: no cover
    _hex_to_unicode = chr

else:
    def _hex_to_unicode(s):
        bytes = b''
        if len(s) % 2 == 1:
            bytes += chr(int(s[0], 16))  # py3: chr() returns unicode
            s = s[1:]
        while s:
            bytes += chr(int(s[:2], 16))  # py3: chr() returns unicode
            s = s[2:]
        while len(bytes) < 4:
            bytes = b'\0' + bytes
        decoder = codecs.getincrementaldecoder('utf_32_be')()
        return decoder.decode(bytes, final=True)
    


#==============================================================================#
def _unescape_ident(m):
    # unescape the substring contained in the Regex match 'm'
    s = m.group('ucs')
    if s:
        cp = int(s, 16)
        if cp <= 0xFFFF:
            return uchr(cp)  # py3: no unichr() function
        else:
            return _hex_to_unicode(s)
    s = m.group('ucs6')
    if s:
        cp = int(s, 16)
        if cp <= 0xFFFF:
            return uchr(cp)  # py3: no unichr() function
        else:
            return _hex_to_unicode(s)
    s = m.group('char')
    if s:
        return s
    raise RuntimeError()
    
def unescape_name(name):
    # Identical to unescape_identifier(). Provided for symmetry with 
    # escape_name().
    return re_unescape_ident.sub(_unescape_ident, name)

def unescape_identifier(ident):
    # \HEX{1,6}WS --> to_unicode(HEX{1,6})
    # \HEX{1,6} --> to_unicode(HEX{1,6})
    # \CHAR --> CHAR
    return re_unescape_ident.sub(_unescape_ident, ident)
    
#==============================================================================#
def _escape_nmstart(m):
    # escape the substring contained in the Regex match 'm'
    s = m.group('digit')
    if s:
        cp = ord(s)
        return u'\\{0:06X}'.format(cp)  # return 6 chars so we don't have to worry about adding a trailing space
    s = m.group('other')
    if s:
        return u'\\{}'.format(s)
    raise RuntimeError()
    
def _escape_nmchar(m):    
    s = m.group('other')
    if s:
        return u'\\{}'.format(s)
    raise RuntimeError()
    
def escape_name(name):
    if not name:
        return name
    return re_escape_nmchar.sub(_escape_nmchar, name)

def escape_identifier(ident):
    # [^-A-Za-z0-9_\xA0-\xFFFFFFFF] -> \CHAR
    # Note: chars that cannot be represented in the current encoding are handled elsewhere.
    if not ident:
        return ident
    if ident[0] == '-':
        return u''.join((
            u'-',
            re_escape_nmstart.sub(_escape_nmstart, ident[1:2]),
            re_escape_nmchar.sub(_escape_nmchar, ident[2:]),
        ))
    else:
        return u''.join((
            re_escape_nmstart.sub(_escape_nmstart, ident[:1]),
            re_escape_nmchar.sub(_escape_nmchar, ident[1:]),
        ))
        
#==============================================================================#
def _unescape_string(m):
    s = m.group('ucs')
    if s:
        cp = int(s, 16)
        if cp <= 0xFFFF:
            return uchr(cp)  # py3: no unichr() function
        else:
            return _hex_to_unicode(s)
    s = m.group('ucs6')
    if s:
        cp = int(s, 16)
        if cp <= 0xFFFF:
            return uchr(cp)  # py3: no unichr() function
        else:
            return _hex_to_unicode(s)
    s = m.group('char')
    if s:
        return s
    s = m.group('nl')
    if s:
        return u''
    raise RuntimeError()

def unescape_string(s):
    # \NEWLINE -> nothing
    # \CHAR -> CHAR
    return re_unescape_string.sub(_unescape_string, s)
    
def unquote_string(s):
    # Remove opening and closing quotes and unescape the contents. The string 
    # should not yet be unescaped.
    assert s[0] == s[-1] and s[0] in ('"', "'")
    return unescape_string(s[1:-1])
    
#==============================================================================#
def escape_string(s, quote_type='double'):
    # \ -> \\
    # quote -> \quote
    # Note: chars that cannot be represented in the current encoding are handled elsewhere.
    if quote_type=='double':
        return re_escape_dquote_string.sub(ur'\\\g<0>', s)
    elif quote_type=='single':
        return re_escape_squote_string.sub(ur'\\\g<0>', s)
    else:
        raise ValueError("Unknown quote_type: '{0}'".format(quote_type))
        
def quote_string(s, quote_type=None):
    # Escape the contents of the string and add opening and closing quotes.
    if quote_type == 'double':
        return u'"{}"'.format(escape_string(s, quote_type))
    elif quote_type == 'single':
        return u"'{}'".format(escape_string(s, quote_type))
    elif '"' in s:
        return u"'{}'".format(escape_string(s, 'single'))
    else:
        return u'"{}"'.format(escape_string(s, 'double'))
    
#==============================================================================#
def css_unicode_error_handler(e):
    if isinstance(e, UnicodeEncodeError):
        u = e.object[e.start:e.end]
        if len(u) == 1:
            cp = ord(u)
            s = u'\\{0:06X}'.format(cp)
            return s, e.end
    raise e
    
def register_unicode_handlers():
    codecs.register_error('cssypy', css_unicode_error_handler)

#==============================================================================#

