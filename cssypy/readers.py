from __future__ import absolute_import
from __future__ import print_function

import re
import codecs
import io

import six

from . import errors, defs

#==============================================================================#
def name8(m):
    return m.group('name')
    
def name16_BE(m):
    raw = m.group('name')
    assert len(raw) % 2 == 0
    return ''.join(c for c in raw[1::2])
    
def name16_LE(m):
    raw = m.group('name')
    assert len(raw) % 2 == 0
    return ''.join(c for c in raw[0::2])
    
def name32_BE(m):
    raw = m.group('name')
    assert len(raw) % 4 == 0
    return ''.join(c for c in raw[3::4])
    
def name32_2143(m): # pragma: no cover
    raw = m.group('name')
    assert len(raw) % 4 == 0
    return ''.join(c for c in raw[2::4])
    
def name32_3412(m): # pragma: no cover
    raw = m.group('name')
    assert len(raw) % 4 == 0
    return ''.join(c for c in raw[1::4])
    
def name32_LE(m):
    raw = m.group('name')
    assert len(raw) % 4 == 0
    return ''.join(c for c in raw[0::4])

#==============================================================================#
def to_16_BE(s):
    return ''.join((r'\x00'+c) for c in s)
def to_16_LE(s):
    return ''.join((c+r'\x00') for c in s)
def to_32_BE(s):
    return ''.join((r'\x00\x00\x00'+c) for c in s)
def to_32_2143(s):
    return ''.join((r'\x00\x00'+c+r'\x00') for c in s)
def to_32_3412(s):
    return ''.join((r'\x00'+c+r'\x00\x00') for c in s)
def to_32_LE(s):
    return ''.join((c+r'\x00\x00\x00') for c in s)

_HEAD = '@charset "'
HEAD_16_BE =    to_16_BE(_HEAD)
HEAD_16_LE =    to_16_LE(_HEAD)
HEAD_32_BE =    to_32_BE(_HEAD)
HEAD_32_2143 =  to_32_2143(_HEAD)
HEAD_32_3412 =  to_32_3412(_HEAD)
HEAD_32_LE =    to_32_LE(_HEAD)

_TAIL = '";'
TAIL_16_BE =    to_16_BE(_TAIL)
TAIL_16_LE =    to_16_LE(_TAIL)
TAIL_32_BE =    to_32_BE(_TAIL)
TAIL_32_2143 =  to_32_2143(_TAIL)
TAIL_32_3412 =  to_32_3412(_TAIL)
TAIL_32_LE =    to_32_LE(_TAIL)
    

#==============================================================================#
# These byte patterns are taken from the CSS2.1 spec.
# The maximum size for one of these patterns should be 212 bytes.
encoding_patterns = (
    # encoding, pattern, is_charset_rule_required
    (name8,    r'^\xEB\xBB\xBF@charset "(?P<name>[^\n\r"]+)";', True),
    ('utf_8',  r'^\xEB\xBB\xBF', False),
    (name8,    r'^@charset "(?P<name>[^\n\r"]+)";', True),
    
    (name16_BE, r'^\xFE\xFF{head}(?P<name>(?:\x00[^\n\r"])+){tail}'.format(head=HEAD_16_BE, tail=TAIL_16_BE), True),
    (name16_BE, r'^{head}(?P<name>(?:\x00[^\n\r"])+){tail}'.format(head=HEAD_16_BE, tail=TAIL_16_BE), True),
    (name16_LE, r'^\xFF\xFE{head}(?P<name>(?:[^\n\r"]\x00)+){tail}'.format(head=HEAD_16_LE, tail=TAIL_16_LE), True),
    (name16_LE, r'^{head}(?P<name>(?:[^\n\r"]\x00)+){tail}'.format(head=HEAD_16_LE, tail=TAIL_16_LE), True),
    
    (name32_BE,   r'^\x00\x00\xFE\xFF{head}(?P<name>(?:\x00\x00\x00[^\n\r"])+){tail}'.format(head=HEAD_32_BE, tail=TAIL_32_BE), True),
    (name32_BE,   r'^{head}(?P<name>(?:\x00\x00\x00[^\n\r"])+){tail}'.format(head=HEAD_32_BE, tail=TAIL_32_BE), True),
    (name32_2143, r'^\x00\x00\xFF\xFE{head}(?P<name>(?:\x00\x00[^\n\r"]\x00)+){tail}'.format(head=HEAD_32_2143, tail=TAIL_32_2143), True),
    (name32_2143, r'^{head}(?P<name>(?:\x00\x00[^\n\r"]\x00)+){tail}'.format(head=HEAD_32_2143, tail=TAIL_32_2143), True),
    (name32_3412, r'^\xFE\xFF\x00\x00{head}(?P<name>(?:\x00[^\n\r"]\x00\x00)+){tail}'.format(head=HEAD_32_3412, tail=TAIL_32_3412), True),
    (name32_3412, r'^{head}(?P<name>(?:\x00[^\n\r"]\x00\x00)+){tail}'.format(head=HEAD_32_3412, tail=TAIL_32_3412), True),
    (name32_LE,   r'^\xFF\xFE\x00\x00{head}(?P<name>(?:[^\n\r"]\x00\x00\x00)+){tail}'.format(head=HEAD_32_LE, tail=TAIL_32_LE), True),
    (name32_LE,   r'^{head}(?P<name>(?:[^\n\r"]\x00\x00\x00)+){tail}'.format(head=HEAD_32_LE, tail=TAIL_32_LE), True),
    
    ('utf_32_be', r'^\x00\x00\xFE\xFF', False),
    ('utf_32_le', r'^\xFF\xFE\x00\x00', False),
    ('utf_32_2143', r'^\x00\x00\xFF\xFE', False),
    ('utf_32_3412', r'^\xFE\xFF\x00\x00', False),
    
    ('utf_16_be', r'^\xFE\xFF', False),
    ('utf_16_le', r'^\xFF\xFE', False),
)

#==============================================================================#
# compile the regexes
encoding_patterns = tuple((enc, re.compile(ptn), req) for (enc,ptn,req) in encoding_patterns)

re_string_charset = re.compile(ur'^@charset "(?P<name>[^\n\r"])";', re.UNICODE)

#==============================================================================#
class Reader(object):
    def __init__(self, filename='<unknown>', default_encoding=None):
        self._filename = filename
        self._default_encoding = default_encoding or defs.DEFAULT_ENCODING
    
    def read(self):
        """Return data as unicode."""
        raise NotImplementedError() # pragma: no cover
    
    def encoding(self):
        raise NotImplementedError() # pragma: no cover
    
    def default_encoding(self):
        return self._default_encoding
    
    def charset_rule_required(self):
        # return true if the parser must parse an apprioriate charset rule 
        # matching the above encoding
        raise NotImplementedError() # pragma: no cover
        
    def filename(self):
        return self._filename
        
    def forced_encoding(self):
        raise NotImplementedError() # pragma: no cover
        
    def _is_known_encoding(self, name):
        try:
            codecinfo = codecs.lookup(name)
            return True
        except LookupError:
            return False
            
    def _bad_encoding_message(self, encoding):
        fmt = 'Cannot read CSS file "{0}". Unknown encoding: "{1}".'
        return fmt.format(self.filename(), encoding)
        
        
#==============================================================================#
class EncodedReader(Reader):
    def __init__(self, filename=None, source_encoding=None, 
                 default_encoding=None):
        filename = filename or '<unknown>'
        super(EncodedReader, self).__init__(filename, default_encoding)
        self.source_encoding = source_encoding
        self._encoding = None
        self._charset_rule_required = False
        self._forced_encoding = source_encoding is not None
    
    def charset_rule_required(self):
        # Reader interface method
        return self._charset_rule_required
        
    def forced_encoding(self):
        return self._forced_encoding
        
    def get_content_for_encoding_check(self, size):
        # read as bytes
        raise NotImplementedError() # pragma: no cover
        
    def encoding_from_content(self, content):
        encoding = None
        for enc, regex, is_charset_rule_required in encoding_patterns:
            m = regex.match(content)
            if m:
                if isinstance(enc, six.string_types):
                    encoding = enc
                else:
                    encoding = enc(m)
                self._charset_rule_required = is_charset_rule_required
                break
        return encoding
        
    def determine_encoding(self):
        encoding = None
        if self.source_encoding:
            encoding = self.source_encoding
        if not encoding:
            content = self.get_content_for_encoding_check(256)
            if content:
                encoding = self.encoding_from_content(content)
        if not encoding:
            encoding = self.default_encoding()
        if not self._is_known_encoding(encoding):
            msg = self._bad_encoding_message(encoding)
            raise errors.CSSEncodingNotFound(msg)
        return encoding
        
    def encoding(self):
        # Reader interface method
        if not self._encoding:
            self._encoding = self.determine_encoding()
        return self._encoding
        
        
#==============================================================================#
class StreamReader(EncodedReader):
    def __init__(self, stream, filename=None, source_encoding=None, 
                 default_encoding=None, do_decoding=True):
        filename = filename or getattr(stream, 'name', '<unknown>')
        super(StreamReader, self).__init__(filename, 
                                           source_encoding=source_encoding, 
                                           default_encoding=default_encoding)
        self.stream = stream
        self.do_decoding = do_decoding
        
    def get_content_for_encoding_check(self, size):
        # Called by base class when determining the encoding used.
        if hasattr(self.stream, 'seekable') and not self.stream.seekable():
            return None
        try:
            cur = self.stream.tell()
            data = self.stream.read(size)
            self.stream.seek(cur)
            return data
        except AttributeError:
            return None
        
    def read(self):
        encoding = self.encoding()
        if self.do_decoding:
            # wrap stream in decoder
            reader = codecs.getreader(encoding)(self.stream)
            return reader.read()
        else:
            return self.stream.read()
        
        
#==============================================================================#
class FileReader(EncodedReader):
    def __init__(self, filename, source_encoding=None, default_encoding=None):
        super(FileReader, self).__init__(filename=filename, 
                                         source_encoding=source_encoding, 
                                         default_encoding=default_encoding)
        
    def get_content_for_encoding_check(self, size):
        # Called by base class when determining the encoding used.
        with open(self.filename(), 'rb') as f:
            return f.read(size)
    
    def read(self):
        encoding = self.encoding()
        # read as encoded stream
        with io.open(self.filename(), mode='rt', encoding=encoding) as f:
            # return unicode
            return f.read()
            

#==============================================================================#
class StringReader(Reader):
    def __init__(self, data, filename='<string>', source_encoding=None, 
                 default_encoding=None):
        super(StringReader, self).__init__(filename, default_encoding)
        self._charset_rule_required = False
        self._encoding = source_encoding
        self._forced_encoding = source_encoding is not None
        self._data = data
        
    def read(self):
        return self._data
        
    def determine_encoding(self):
        m = re_string_charset.match(self._data)
        if m:
            encoding = m.group('name')
            if not self._is_known_encoding(encoding):
                msg = self._bad_encoding_message(encoding)
                raise errors.CSSEncodingNotFound(msg)
            self._charset_rule_required = True
            return encoding
        return self.default_encoding()
        
    def encoding(self):
        if not self._encoding:
            self._encoding = self.determine_encoding()
        return self._encoding
        
    def charset_rule_required(self):
        return self._charset_rule_required
        
    def forced_encoding(self):
        return self._forced_encoding
        

#==============================================================================#
