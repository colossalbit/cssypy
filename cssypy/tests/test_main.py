from cssypy import main

from . import base

#==============================================================================#
class Main_TestCase(base.TestCaseBase):
    def test_empty(self):
        src = ''
        ifilename = self.create_tempfile(data=src, suffix='.css')
        ofilename = self.create_tempfile(suffix='.css')
        cmdline = [ifilename, ofilename]
        main._main(cmdline=cmdline)
        with open(ofilename, 'r') as f:
            output = f.read()
        self.assertEqual(u'', output)


#==============================================================================#

