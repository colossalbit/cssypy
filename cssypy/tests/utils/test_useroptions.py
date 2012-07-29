import textwrap

from cssypy.utils import useroptions

from .. import base

Opt = useroptions.OptionDef


class OptionSpec_TestCase(base.TestCaseBase):
    def test_cmdline_helper(self):
        # The kwarg 'cmdline_helper' means the option is only an implementation 
        # detail for the cmdline parser. Such an option should not be available 
        # in the options dictionary returned by the OptionsReader.
        optspec = useroptions.OptionSpec()
        optspec.add_optdef(Opt('enable_x', action='store_true', dest='enable_x', default=True))
        optspec.add_optdef(Opt('disable_x', action='store_false', dest='enable_x', cmdline_helper=True))
        
        cmdline = ['--enable-x']
        optsreader = useroptions.OptionsReader(optspec)
        optdict = optsreader.get_options(cmdline=cmdline)
        self.assertTrue('disable_x' not in optdict)
        self.assertEqual(True, optdict['enable_x'])
        
        cmdline = ['--disable-x']
        optsreader = useroptions.OptionsReader(optspec)
        optdict = optsreader.get_options(cmdline=cmdline)
        self.assertTrue('disable_x' not in optdict)
        self.assertEqual(False, optdict['enable_x'])
        
    def test_configfile(self):
        data = """\
        [General]
        abc=xyz
        def=jkl
        """
        data = textwrap.dedent(data)
        filename = self.create_tempfile(data=data)
        
        optspec = useroptions.OptionSpec()
        optspec.add_optdef(Opt('abc'))
        optspec.add_optdef(Opt('def'))
        
        cmdline = []
        optsreader = useroptions.OptionsReader(optspec)
        optdict = optsreader.get_options(cmdline=cmdline, config_filename=filename)
        self.assertEqual('xyz', optdict['abc'])
        self.assertEqual('jkl', optdict['def'])
        
    def test_default(self):
        optspec = useroptions.OptionSpec()
        optspec.add_optdef(Opt('abc', default='123'))
        
        cmdline = []
        optsreader = useroptions.OptionsReader(optspec)
        optdict = optsreader.get_options(cmdline=cmdline)
        self.assertEqual('123', optdict['abc'])
        

class OptionDef_TestCase(base.TestCaseBase):
    def test_configfile_conv(self):
        opt = useroptions.OptionDef('x')
        self.assertEquals('85.6', opt.configfile_conv('85.6'))
        
        opt = useroptions.OptionDef('x', type=bool)
        self.assertEquals(True, opt.configfile_conv('T'))
        self.assertEquals(False, opt.configfile_conv('F'))
        self.assertEquals(True, opt.configfile_conv('on'))
        self.assertEquals(False, opt.configfile_conv('0'))
        
        opt = useroptions.OptionDef('x', type=int)
        self.assertEquals(55, opt.configfile_conv('55'))
        self.assertEquals(-1, opt.configfile_conv('-1'))
        
        opt = useroptions.OptionDef('x', type=int, list=True)
        self.assertEquals([1,2,6], opt.configfile_conv('1,2,6'))
        self.assertEquals([0,-1,99], opt.configfile_conv('0,-1 ,  99  '))
        
    def test_default(self):
        opt = useroptions.OptionDef('x')
        self.assertEquals(None, opt.get_default())
        
        opt = useroptions.OptionDef('x', list=True)
        self.assertEquals([], opt.get_default())
        
        
