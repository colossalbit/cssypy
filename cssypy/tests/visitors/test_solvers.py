from cssypy.visitors import solvers
from cssypy import parsers, errors
from cssypy import csstokens as tokens
from cssypy.nodes.util import dump
from cssypy.nodes import *

from .. import base


class Solver_TestCase(base.TestCaseBase):
    def test_add_numbers(self):
        src = u'prop: 1+2 ;'
        parser = parsers.Parser(src)
        self.assertTrue(parser.match(tokens.START))
        decl = parser.declaration()
        solver = solvers.Solver()
        decl = solver.visit(decl)
        expected = \
            Declaration(
                prop=Property(name=u'prop'),
                expr=NumberNode(number=u'3'),
                important=False,
            )
        self.assertEqual(dump(expected), dump(decl))
        
    def test_add_dimensions1(self):
        src = u'prop: 1px+2px ;'
        parser = parsers.Parser(src)
        self.assertTrue(parser.match(tokens.START))
        decl = parser.declaration()
        solver = solvers.Solver()
        decl = solver.visit(decl)
        expected = \
            Declaration(
                prop=Property(name=u'prop'),
                expr=DimensionNode(number=u'3', unit=u'px'),
                important=False,
            )
        self.assertEqual(dump(expected), dump(decl))
        
    def test_add_dimensions2(self):
        src = u'prop: 1px+1in ;'
        parser = parsers.Parser(src)
        self.assertTrue(parser.match(tokens.START))
        decl = parser.declaration()
        solver = solvers.Solver()
        decl = solver.visit(decl)
        expected = \
            Declaration(
                prop=Property(name=u'prop'),
                expr=DimensionNode(number=u'97', unit=u'px'),
                important=False,
            )
        self.assertEqual(dump(expected), dump(decl))
        
    def test_subtract_dimensions1(self):
        src = u'prop: (6px - 2px) ;'
        parser = parsers.Parser(src)
        self.assertTrue(parser.match(tokens.START))
        decl = parser.declaration()
        solver = solvers.Solver()
        decl = solver.visit(decl)
        expected = \
            Declaration(
                prop=Property(name=u'prop'),
                expr=DimensionNode(number=u'4', unit=u'px'),
                important=False,
            )
        self.assertEqual(dump(expected), dump(decl))
        
    def test_subtract_dimensions2(self):
        src = u'prop: (99px - 1in) ;'
        parser = parsers.Parser(src)
        self.assertTrue(parser.match(tokens.START))
        decl = parser.declaration()
        solver = solvers.Solver()
        decl = solver.visit(decl)
        expected = \
            Declaration(
                prop=Property(name=u'prop'),
                expr=DimensionNode(number=u'3', unit=u'px'),
                important=False,
            )
        self.assertEqual(dump(expected), dump(decl))
        
    def test_add_incompatible_dimensions(self):
        src = u'prop: 1px+1em ;'
        parser = parsers.Parser(src)
        self.assertTrue(parser.match(tokens.START))
        decl = parser.declaration()
        solver = solvers.Solver()
        with self.assertRaises(errors.CSSTypeError):
            solver.visit(decl)
        
    def test_add_dimension_number(self):
        src = u'prop: 1px+1 ;'
        parser = parsers.Parser(src)
        self.assertTrue(parser.match(tokens.START))
        decl = parser.declaration()
        solver = solvers.Solver()
        decl = solver.visit(decl)
        expected = \
            Declaration(
                prop=Property(name=u'prop'),
                expr=DimensionNode(number=u'2', unit=u'px'),
                important=False,
            )
        self.assertEqual(dump(expected), dump(decl))
        
    def test_add_number_dimension(self):
        src = u'prop: 1+1px ;'
        parser = parsers.Parser(src)
        self.assertTrue(parser.match(tokens.START))
        decl = parser.declaration()
        solver = solvers.Solver()
        decl = solver.visit(decl)
        expected = \
            Declaration(
                prop=Property(name=u'prop'),
                expr=DimensionNode(number=u'2', unit=u'px'),
                important=False,
            )
        self.assertEqual(dump(expected), dump(decl))
    
    def test_negated1(self):
        src = u'prop: -1 ;'
        parser = parsers.Parser(src)
        self.assertTrue(parser.match(tokens.START))
        decl = parser.declaration()
        solver = solvers.Solver()
        decl = solver.visit(decl)
        expected = \
            Declaration(
                prop=Property(name=u'prop'),
                expr=UnaryOpExpr(
                    op=UMinus(),
                    operand=NumberNode(number=u'1'),
                ),
                important=False,
            )
        self.assertEqual(dump(expected), dump(decl))
    
    def test_negated2(self):
        src = u'prop: -1+3;'
        parser = parsers.Parser(src)
        self.assertTrue(parser.match(tokens.START))
        decl = parser.declaration()
        solver = solvers.Solver()
        decl = solver.visit(decl)
        expected = \
            Declaration(
                prop=Property(name=u'prop'),
                expr=NumberNode(number=u'2'),
                important=False,
            )
        self.assertEqual(dump(expected), dump(decl))
    
    def test_negated_expr(self):
        src = u'prop: -(1 + 2) ;'
        parser = parsers.Parser(src)
        self.assertTrue(parser.match(tokens.START))
        decl = parser.declaration()
        solver = solvers.Solver()
        decl = solver.visit(decl)
        expected = \
            Declaration(
                prop=Property(name=u'prop'),
                expr=UnaryOpExpr(
                    op=UMinus(),
                    operand=NumberNode(number=u'3'),
                ),
                important=False,
            )
        self.assertEqual(dump(expected), dump(decl))



