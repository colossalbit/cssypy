import codecs
from StringIO import StringIO

from cssypy.utils import escapes

from .. import base

class quote_string_TestCase(base.TestCaseBase):
    def test_empty(self):
        self.assertEqual(u'""', escapes.quote_string(u''))
        
    def test_embedded_squote(self):
        self.assertEqual(u'"a\'b"', escapes.quote_string(u'a\'b'))
        
    def test_embedded_dquote(self):
        self.assertEqual(u"'a\"b'", escapes.quote_string(u'a"b'))
        

class unquote_string_TestCase(base.TestCaseBase):
    def test_empty(self):
        self.assertEqual(u'', escapes.unquote_string(u'""'))
        self.assertEqual(u'', escapes.unquote_string(u"''"))
        
    def test_embedded_css_escapes(self):
        self.assertEqual(u" ", escapes.unquote_string(u'"\\20"'))
        self.assertEqual(u"\uABCD", escapes.unquote_string(u'"\\ABCD"'))
        self.assertEqual(u"\uABCD", escapes.unquote_string(u'"\\00ABCD"'))
        self.assertEqual(u"X", escapes.unquote_string(u'"\\X"'))
        # BACKSLASH NEWLINE
        self.assertEqual(u"", escapes.unquote_string(u'"\\\n"'))
        

class escape_identifier_TestCase(base.TestCaseBase):
    def test_simple(self):
        self.assertEqual(u'abc', escapes.escape_identifier(u'abc'))
        self.assertEqual(u'abc2', escapes.escape_identifier(u'abc2'))
        self.assertEqual(u'abc-', escapes.escape_identifier(u'abc-'))
        self.assertEqual(u'ab-c', escapes.escape_identifier(u'ab-c'))
        self.assertEqual(u'a-bc', escapes.escape_identifier(u'a-bc'))
        self.assertEqual(u'-abc', escapes.escape_identifier(u'-abc'))
    
    def test_special_chars(self):
        self.assertEqual(u'ab\\{c', escapes.escape_identifier(u'ab{c'))
        self.assertEqual(u'\\000036abc', escapes.escape_identifier(u'6abc'))
        self.assertEqual(u'\\{abc', escapes.escape_identifier(u'{abc'))
        self.assertEqual(u'a\\\\bc', escapes.escape_identifier(u'a\\bc'))
        self.assertEqual(u'abc\\.', escapes.escape_identifier(u'abc.'))
        

class unescape_identifier_TestCase(base.TestCaseBase):
    def test_simple(self):
        self.assertEqual(u'abc', escapes.unescape_identifier(u'abc'))
        self.assertEqual(u'abc2', escapes.unescape_identifier(u'abc2'))
        self.assertEqual(u'abc-', escapes.unescape_identifier(u'abc-'))
        self.assertEqual(u'ab-c', escapes.unescape_identifier(u'ab-c'))
        self.assertEqual(u'a-bc', escapes.unescape_identifier(u'a-bc'))
        self.assertEqual(u'-abc', escapes.unescape_identifier(u'-abc'))
        
    def test_special_chars(self):
        self.assertEqual(u'ab{c', escapes.unescape_identifier(u'ab\\{c'))
        self.assertEqual(u'6abc', escapes.unescape_identifier(u'\\000036abc'))
        self.assertEqual(u'{abc', escapes.unescape_identifier(u'\\{abc'))
        self.assertEqual(u'a\\bc', escapes.unescape_identifier(u'a\\\\bc'))
        self.assertEqual(u'abc.', escapes.unescape_identifier(u'abc\\.'))
        

class css_unicode_error_handler_TestCase(base.TestCaseBase):
    def test_basic(self):
        codecs.register_error('cssypy', escapes.css_unicode_error_handler)
        Writer = codecs.getwriter('ascii')
        stream = StringIO()
        writer = Writer(stream, errors='cssypy')
        writer.write(u'abcdefg')
        self.assertEqual('abcdefg', stream.getvalue())
        
    def test_bmp(self):
        codecs.register_error('cssypy', escapes.css_unicode_error_handler)
        Writer = codecs.getwriter('ascii')
        stream = StringIO()
        writer = Writer(stream, errors='cssypy')
        writer.write(u'ab\uABCDcd')
        self.assertEqual('ab\\00ABCDcd', stream.getvalue())
        

