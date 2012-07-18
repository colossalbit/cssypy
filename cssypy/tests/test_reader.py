from cStringIO import StringIO
import codecs

from cssypy import readers

from . import base

class StreamReader_TestCase(base.TestCaseBase):
    def test_empty(self):
        stream = StringIO('')
        reader = readers.StreamReader(stream, default_encoding='utf_8')
        self.assertEquals('utf_8', reader.encoding())
        self.assertEquals(False, reader.charset_rule_required())
        self.assertEquals(False, reader.forced_encoding())
        
    def test_force_encoding1(self):
        stream = StringIO('')
        reader = readers.StreamReader(stream, source_encoding='latin1')
        self.assertEquals('latin1', reader.encoding())
        self.assertEquals(False, reader.charset_rule_required())
        self.assertEquals(True, reader.forced_encoding())
        
    def test_force_encoding2(self):
        stream = StringIO('@charset "utf_8";\nthis_is_ignored {}')
        reader = readers.StreamReader(stream, source_encoding='latin1')
        self.assertEquals('latin1', reader.encoding())
        self.assertEquals(False, reader.charset_rule_required())
        self.assertEquals(True, reader.forced_encoding())
        
    def test_charset_8bit(self):
        stream = StringIO('@charset "utf_8";\nthis_is_ignored {}')
        reader = readers.StreamReader(stream, default_encoding='latin1')
        self.assertEquals('utf_8', reader.encoding())
        self.assertEquals(True, reader.charset_rule_required())
        self.assertEquals(False, reader.forced_encoding())
        
    def test_charset_16bit(self):
        s = u'@charset "utf_16";\nthis_is_ignored {}'
        s = bytes(s.encode('utf-16'))
        self.assertTrue(s[0] == '\xFF' or s[0] == '\xFE')  # BOM sanity check
        stream = StringIO(s)
        reader = readers.StreamReader(stream, default_encoding='latin1')
        self.assertEquals('utf_16', reader.encoding())
        self.assertEquals(True, reader.charset_rule_required())
        self.assertEquals(False, reader.forced_encoding())
        
    def test_charset_16bit_no_bom(self):
        s = u'@charset "utf_16";\nthis_is_ignored {}'
        s = bytes(s.encode('utf-16'))
        self.assertTrue(s[0] == '\xFF' or s[0] == '\xFE')  # BOM sanity check
        s = s[2:]  # strip the BOM
        stream = StringIO(s)
        reader = readers.StreamReader(stream, default_encoding='latin1')
        self.assertEquals('utf_16', reader.encoding())
        self.assertEquals(True, reader.charset_rule_required())
        self.assertEquals(False, reader.forced_encoding())
        
        
