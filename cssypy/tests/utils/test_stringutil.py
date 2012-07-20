import codecs
from StringIO import StringIO

from cssypy.utils import stringutil

from .. import base

class quote_string_TestCase(base.TestCaseBase):
    def test_empty(self):
        self.assertEqual(u'""', stringutil.quote_string(u''))
        
    def test_embedded_squote(self):
        self.assertEqual(u'"a\'b"', stringutil.quote_string(u'a\'b'))
        
    def test_embedded_dquote(self):
        self.assertEqual(u"'a\"b'", stringutil.quote_string(u'a"b'))
        

class unquote_string_TestCase(base.TestCaseBase):
    def test_empty(self):
        self.assertEqual(u'', stringutil.unquote_string(u'""'))
        self.assertEqual(u'', stringutil.unquote_string(u"''"))
        
    def test_embedded_css_escapes(self):
        self.assertEqual(u" ", stringutil.unquote_string(u'"\\20"'))
        self.assertEqual(u"\uABCD", stringutil.unquote_string(u'"\\ABCD"'))
        self.assertEqual(u"\uABCD", stringutil.unquote_string(u'"\\00ABCD"'))
        self.assertEqual(u"X", stringutil.unquote_string(u'"\\X"'))
        # BACKSLASH NEWLINE
        self.assertEqual(u"", stringutil.unquote_string(u'"\\\n"'))
        

class escape_identifier_TestCase(base.TestCaseBase):
    def test_simple(self):
        self.assertEqual(u'abc', stringutil.escape_identifier(u'abc'))
        self.assertEqual(u'abc2', stringutil.escape_identifier(u'abc2'))
        self.assertEqual(u'abc-', stringutil.escape_identifier(u'abc-'))
        self.assertEqual(u'ab-c', stringutil.escape_identifier(u'ab-c'))
        self.assertEqual(u'a-bc', stringutil.escape_identifier(u'a-bc'))
        self.assertEqual(u'-abc', stringutil.escape_identifier(u'-abc'))
    
    def test_special_chars(self):
        self.assertEqual(u'ab\\{c', stringutil.escape_identifier(u'ab{c'))
        self.assertEqual(u'\\000036abc', stringutil.escape_identifier(u'6abc'))
        self.assertEqual(u'\\{abc', stringutil.escape_identifier(u'{abc'))
        self.assertEqual(u'a\\\\bc', stringutil.escape_identifier(u'a\\bc'))
        self.assertEqual(u'abc\\.', stringutil.escape_identifier(u'abc.'))
        

class unescape_identifier_TestCase(base.TestCaseBase):
    def test_simple(self):
        self.assertEqual(u'abc', stringutil.unescape_identifier(u'abc'))
        self.assertEqual(u'abc2', stringutil.unescape_identifier(u'abc2'))
        self.assertEqual(u'abc-', stringutil.unescape_identifier(u'abc-'))
        self.assertEqual(u'ab-c', stringutil.unescape_identifier(u'ab-c'))
        self.assertEqual(u'a-bc', stringutil.unescape_identifier(u'a-bc'))
        self.assertEqual(u'-abc', stringutil.unescape_identifier(u'-abc'))
        
    def test_special_chars(self):
        self.assertEqual(u'ab{c', stringutil.unescape_identifier(u'ab\\{c'))
        self.assertEqual(u'6abc', stringutil.unescape_identifier(u'\\000036abc'))
        self.assertEqual(u'{abc', stringutil.unescape_identifier(u'\\{abc'))
        self.assertEqual(u'a\\bc', stringutil.unescape_identifier(u'a\\\\bc'))
        self.assertEqual(u'abc.', stringutil.unescape_identifier(u'abc\\.'))
        

class css_unicode_error_handler_TestCase(base.TestCaseBase):
    def test_basic(self):
        codecs.register_error('cssypy', stringutil.css_unicode_error_handler)
        Writer = codecs.getwriter('ascii')
        stream = StringIO()
        writer = Writer(stream, errors='cssypy')
        writer.write(u'abcdefg')
        self.assertEqual('abcdefg', stream.getvalue())
        
    def test_bmp(self):
        codecs.register_error('cssypy', stringutil.css_unicode_error_handler)
        Writer = codecs.getwriter('ascii')
        stream = StringIO()
        writer = Writer(stream, errors='cssypy')
        writer.write(u'ab\uABCDcd')
        self.assertEqual('ab\\00ABCDcd', stream.getvalue())
        

