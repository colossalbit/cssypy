from __future__ import absolute_import
from __future__ import print_function

import six

from .. import readers, stylesheets

#==============================================================================#
class ParserWrapper(object):
    default_encoding = None
    
    def __init__(self, Parser, default_encoding=None):
        self.default_encoding = default_encoding or self.default_encoding
        self.Parser = Parser
    
    def _parse(self, reader):
        parser = self.Parser(reader.read())
        rootnode = parser.parse()
        if reader.charset_rule_required():
            # check that rootnode contains an appropriate @charset rule
            pass
        return stylesheets.Stylesheet(rootnode, 
                                      filename=reader.filename(), 
                                      encoding=reader.encoding(), 
                                      forced_encoding=reader.forced_encoding(), 
                                      Parser=self.Parser)
                           
    def parse(self, file, filename=None, source_encoding=None, default_encoding=None, do_decoding=True):
        if isinstance(file, six.string_types):
            return self.parse_file(file, source_encoding=source_encoding, 
                                   default_encoding=default_encoding)
        else:
            return self.parse_stream(file, filename=filename, 
                                     source_encoding=source_encoding, 
                                     default_encoding=default_encoding,
                                     do_decoding=do_decoding)
        
    def parse_file(self, filename, source_encoding=None, default_encoding=None):
        default_encoding = default_encoding or self.default_encoding
        reader = readers.FileReader(filename, source_encoding=source_encoding, 
                                    default_encoding=default_encoding)
        return self._parse(reader)
                           
    def parse_stream(self, stream, filename=None, source_encoding=None, default_encoding=None, do_decoding=True):
        default_encoding = default_encoding or self.default_encoding
        reader = readers.StreamReader(stream, filename=filename,
                                      source_encoding=source_encoding,
                                      default_encoding=default_encoding, 
                                      do_decoding=do_decoding)
        return self._parse(reader)
                                     
    def parse_string(self, data, filename='<string>', source_encoding=None, default_encoding=None):
        default_encoding = default_encoding or self.default_encoding
        if not isinstance(data, six.text_type):
            raise ValueError()
        reader = readers.StringReader(data, filename=filename, 
                                      source_encoding=source_encoding, 
                                      default_encoding=default_encoding)
        return self._parse(reader)


#==============================================================================#

