from cStringIO import StringIO

from cssypy.utils import reporters

from .. import base


class ReporterBase_TestCase(base.TestCaseBase):
    def test_basic(self):
        err = StringIO()
        out = StringIO()
        reporter = reporters.ReporterBase(error_stream=err, std_stream=out, level=reporters.INFO)
        reporter.critical('critical')
        reporter.error('error')
        reporter.warning('warning')
        reporter.info('info')
        reporter.debug('debug')
        
        self.assertEqual('info\n', out.getvalue())
        self.assertEqual('critical\nerror\nwarning\n', err.getvalue())

