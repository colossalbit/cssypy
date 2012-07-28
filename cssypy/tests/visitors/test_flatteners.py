import textwrap
import io

from cssypy.visitors import flatteners, formatters
from cssypy import parsers, errors
from cssypy import csstokens as tokens
from cssypy.nodes.util import dump
from cssypy.nodes import *

from .. import base


class Flattener_TestCase(base.TestCaseBase):
    def stylesheet_to_string(self, stylesheet):
        stream = io.StringIO()
        formatter = formatters.CSSFormatterVisitor(stream)
        formatter.visit(stylesheet)
        return stream.getvalue()
    
    def test_simple(self):
        src = u'a {}'
        parser = parsers.Parser(src)
        self.assertTrue(parser.match(tokens.START))
        stylesheet = parser.stylesheet()
        flattener = flatteners.RulesetFlattener()
        stylesheet = flattener.visit(stylesheet)
        expected = \
            Stylesheet(
                charset=None,
                imports=[],
                statements=[
                    RuleSet(
                        selectors=[
                            Selector(
                                children=[
                                    SimpleSelectorSequence(
                                        head=TypeSelector(name=u'a'),
                                        tail=[]
                                    )
                                ]
                            ),
                        ],
                        statements=[]
                    ),
                ]
            )
        self.assertEqual(dump(expected), dump(stylesheet))
        
    def test_two_level(self):
        src = u'a { b {} } '
        expect = u'''\
        a {}
        a b {}
        '''
        expect = textwrap.dedent(expect)
        
        parser = parsers.Parser(src)
        self.assertTrue(parser.match(tokens.START))
        stylesheet = parser.stylesheet()
        flattener = flatteners.RulesetFlattener()
        stylesheet = flattener.visit(stylesheet)
        result = self.stylesheet_to_string(stylesheet)
        
        self.assertEqual(expect, result)
        
    def test_four_level(self):
        src = u'a { b { c { d {} } } } '
        expect = u'''\
        a {}
        a b {}
        a b c {}
        a b c d {}
        '''
        expect = textwrap.dedent(expect)
        
        parser = parsers.Parser(src)
        self.assertTrue(parser.match(tokens.START))
        stylesheet = parser.stylesheet()
        flattener = flatteners.RulesetFlattener()
        stylesheet = flattener.visit(stylesheet)
        result = self.stylesheet_to_string(stylesheet)
        
        self.assertEqual(expect, result)
        
    def test_comma_separated1(self):
        src = u'''\
        a, b {
            c, d {}
        }
        '''
        expect = u'''\
        a, b {}
        a c, b c, a d, b d {}
        '''
        expect = textwrap.dedent(expect)
        
        parser = parsers.Parser(src)
        self.assertTrue(parser.match(tokens.START))
        stylesheet = parser.stylesheet()
        flattener = flatteners.RulesetFlattener()
        stylesheet = flattener.visit(stylesheet)
        result = self.stylesheet_to_string(stylesheet)
        
        self.assertEqual(expect, result)
        
    def test_comma_separated2(self):
        src = u'''\
        a b, c {
            d, e f {}
        }
        '''
        expect = u'''\
        a b, c {}
        a b d, c d, a b e f, c e f {}
        '''
        expect = textwrap.dedent(expect)
        
        parser = parsers.Parser(src)
        self.assertTrue(parser.match(tokens.START))
        stylesheet = parser.stylesheet()
        flattener = flatteners.RulesetFlattener()
        stylesheet = flattener.visit(stylesheet)
        result = self.stylesheet_to_string(stylesheet)
        
        self.assertEqual(expect, result)
        
    def test_ancestor_selector1(self):
        src = u'''\
        a {
            &>b {}
        }
        '''
        expect = u'''\
        a {}
        a > b {}
        '''
        expect = textwrap.dedent(expect)
        
        parser = parsers.Parser(src)
        self.assertTrue(parser.match(tokens.START))
        stylesheet = parser.stylesheet()
        flattener = flatteners.RulesetFlattener()
        stylesheet = flattener.visit(stylesheet)
        result = self.stylesheet_to_string(stylesheet)
        
        self.assertEqual(expect, result)
        
    def test_ancestor_selector2(self):
        src = u'''\
        .a {
            b & c {}
        }
        '''
        expect = u'''\
        .a {}
        b .a c {}
        '''
        expect = textwrap.dedent(expect)
        
        parser = parsers.Parser(src)
        self.assertTrue(parser.match(tokens.START))
        stylesheet = parser.stylesheet()
        flattener = flatteners.RulesetFlattener()
        stylesheet = flattener.visit(stylesheet)
        result = self.stylesheet_to_string(stylesheet)
        
        self.assertEqual(expect, result)
        
    def test_ancestor_selector3(self):
        src = u'''\
        a {
            &.b:c {}
        }
        '''
        expect = u'''\
        a {}
        a.b:c {}
        '''
        expect = textwrap.dedent(expect)
        
        parser = parsers.Parser(src)
        self.assertTrue(parser.match(tokens.START))
        stylesheet = parser.stylesheet()
        flattener = flatteners.RulesetFlattener()
        stylesheet = flattener.visit(stylesheet)
        result = self.stylesheet_to_string(stylesheet)
        
        self.assertEqual(expect, result)




