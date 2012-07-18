import unittest
import tempfile
import os


class TestCaseBase(unittest.TestCase):
    def setUp(self):
        super(TestCaseBase, self).setUp()
        self.tempfiles = []
        
    def tearDown(self):
        for filename in self.tempfiles:
            try:
                os.remove(filename)
            except IOError as e:
                print 'TestCaseBase: Error deleting temp file: {}'.format(str(e))
        self.tempfiles = []
        super(TestCaseBase, self).tearDown()
        
    def create_tempfile(self, data=None, suffix='', prefix='tmp'):
        with tempfile.NamedTemporaryFile(suffix=suffix, prefix=prefix, delete=False) as f:
            if data:
                f.write(data)
            name = f.name
            self.tempfiles.append(name)
        return name



