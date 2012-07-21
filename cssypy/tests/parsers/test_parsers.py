from cssypy.parsers import Parser
from cssypy import csstokens as tokens
from cssypy.nodes.util import dump
from cssypy.nodes import *

from .. import base

#==============================================================================#
class Parser_TestCase(base.TestCaseBase):
    def test_empty(self):
        src = u''
        parser = Parser(src)
        stylesheet = parser.parse()
        self.assertEqual('Stylesheet(charset=None, imports=[], statements=[])', dump(stylesheet))
        
    def test_charset(self):
        src = u'@charset "utf-8";'
        parser = Parser(src)
        stylesheet = parser.parse()
        self.assertEqual("Stylesheet(charset=Charset(charset=u'utf-8'), imports=[], statements=[])", dump(stylesheet))
        
        
#==============================================================================#
class MathExprOperator_TestCase(base.TestCaseBase):
    def test_simple(self):
        src = u' + '
        parser = Parser(src)
        self.assertTrue(parser.match(tokens.START))
        op = parser.math_expr_operator()
        self.assertTrue(op is not None)
        self.assertEqual("AddOp()", dump(op))
        
        
#==============================================================================#
class CommaExpression_TestCase(base.TestCaseBase):
    def test_empty(self):
        src = u''
        parser = Parser(src)
        expr = parser.comma_expr()
        self.assertEqual(None, expr)
        
    def test_ident(self):
        src = u'abc '
        parser = Parser(src)
        self.assertTrue(parser.match(tokens.START))
        expr = parser.comma_expr()
        self.assertEqual("IdentExpr(name=u'abc')", dump(expr))
        
    def test_hash(self):
        src = u'#aabbcc '
        parser = Parser(src)
        self.assertTrue(parser.match(tokens.START))
        expr = parser.comma_expr()
        self.assertEqual("HexColorNode(hex=u'aabbcc')", dump(expr))
        
    def test_plus(self):
        src = u'$a+$b'
        parser = Parser(src)
        self.assertTrue(parser.match(tokens.START))
        expr = parser.comma_expr()
        self.assertEqual("BinaryOpExpr(op=AddOp(), lhs=VarName(name=u'a'), rhs=VarName(name=u'b'))", dump(expr))
        
    def test_plus1(self):
        src = u'$a + $b'
        parser = Parser(src)
        self.assertTrue(parser.match(tokens.START))
        expr = parser.comma_expr()
        self.assertEqual("VarName(name=u'a')", dump(expr))
        
    def test_plus2(self):
        src = u'($a + $b)'
        parser = Parser(src)
        self.assertTrue(parser.match(tokens.START))
        expr = parser.comma_expr()
        self.assertEqual("BinaryOpExpr(op=AddOp(), lhs=VarName(name=u'a'), rhs=VarName(name=u'b'))", dump(expr))
        
    def test_usub(self):
        src = '$a -$b'
        parser = Parser(src)
        self.assertTrue(parser.match(tokens.START))
        expr = parser.comma_expr()
        expected = NaryOpExpr(
                        op=WhitespaceOp(), 
                        operands=[
                            VarName(name='a'), 
                            UnaryOpExpr(op=UMinus(), 
                                        operand=VarName(name='b')
                            )
                        ]
                    )
        ##expected = "NaryOpExpr(op=WhitespaceOp(), operands=[VarName(name='a'), UnaryOpExpr(op=UMinus(), operand=VarName(name='b'))])"
        self.assertEqual(expected, expr)
        
    def test_precedence1(self):
        src = '$a+$b*$c'
        parser = Parser(src)
        self.assertTrue(parser.match(tokens.START))
        expr = parser.comma_expr()
        expected = BinaryOpExpr(
                        op=AddOp(),
                        lhs=VarName(name='a'),
                        rhs=BinaryOpExpr(
                            op=MultOp(),
                            lhs=VarName(name='b'),
                            rhs=VarName(name='c')
                        )
                   )
        self.assertEqual(dump(expected), dump(expr))
        
    def test_precedence2(self):
        src = '$a*$b+$c'
        parser = Parser(src)
        self.assertTrue(parser.match(tokens.START))
        expr = parser.comma_expr()
        expected = BinaryOpExpr(
                        op=AddOp(),
                        lhs=BinaryOpExpr(
                            op=MultOp(),
                            lhs=VarName(name='a'),
                            rhs=VarName(name='b')
                        ),
                        rhs=VarName(name='c')
                   )
        self.assertEqual(dump(expected), dump(expr))
        
    def test_precedence3(self):
        src = '$a+$b*$c+($d - $e)'
        parser = Parser(src)
        self.assertTrue(parser.match(tokens.START))
        expr = parser.comma_expr()
        expected = BinaryOpExpr(
                        op=AddOp(),
                        lhs=BinaryOpExpr(
                            op=AddOp(),
                            lhs=VarName(name='a'),
                            rhs=BinaryOpExpr(
                                op=MultOp(),
                                lhs=VarName(name='b'),
                                rhs=VarName(name='c')
                            )
                        ),
                        rhs=BinaryOpExpr(
                            op=SubtractOp(),
                            lhs=VarName(name='d'),
                            rhs=VarName(name='e')
                        )
                   )
        self.assertEqual(dump(expected), dump(expr))
        
    def test_precedence4(self):
        src = '$a+$b+$c'
        parser = Parser(src)
        self.assertTrue(parser.match(tokens.START))
        expr = parser.comma_expr()
        expected = BinaryOpExpr(
                        op=AddOp(),
                        lhs=BinaryOpExpr(
                            op=AddOp(),
                            lhs=VarName(name='a'),
                            rhs=VarName(name='b')
                        ),
                        rhs=VarName(name='c')
                   )
        self.assertEqual(dump(expected), dump(expr))
        
    def test_whitespaceop(self):
        src = '$a $b $c'
        parser = Parser(src)
        self.assertTrue(parser.match(tokens.START))
        expr = parser.comma_expr()
        expected = NaryOpExpr(
                        op=WhitespaceOp(),
                        operands=[
                            VarName(name='a'),
                            VarName(name='b'),
                            VarName(name='c'),
                        ]
                   )
        self.assertEqual(dump(expected), dump(expr))
        
    def test_whitespaceop2(self):
        src = '$a $b $c $d'
        parser = Parser(src)
        self.assertTrue(parser.match(tokens.START))
        expr = parser.comma_expr()
        expected = NaryOpExpr(
                        op=WhitespaceOp(),
                        operands=[
                            VarName(name='a'),
                            VarName(name='b'),
                            VarName(name='c'),
                            VarName(name='d'),
                        ]
                   )
        self.assertEqual(dump(expected), dump(expr))
        
    def test_whitespaceop3(self):
        src = '$a $b $c+$d'
        parser = Parser(src)
        self.assertTrue(parser.match(tokens.START))
        expr = parser.comma_expr()
        expected = NaryOpExpr(
                        op=WhitespaceOp(),
                        operands=[
                            VarName(name='a'),
                            VarName(name='b'),
                            BinaryOpExpr(
                                op=AddOp(),
                                lhs=VarName(name='c'),
                                rhs=VarName(name='d'),
                            ),
                        ]
                   )
        self.assertEqual(dump(expected), dump(expr))
        
    def test_whitespaceop4(self):
        src = '$a+$b $c $d'
        parser = Parser(src)
        self.assertTrue(parser.match(tokens.START))
        expr = parser.comma_expr()
        expected = NaryOpExpr(
                        op=WhitespaceOp(),
                        operands=[
                            BinaryOpExpr(
                                op=AddOp(),
                                lhs=VarName(name='a'),
                                rhs=VarName(name='b'),
                            ),
                            VarName(name='c'),
                            VarName(name='d'),
                        ]
                   )
        self.assertEqual(dump(expected), dump(expr))
        
    def test_whitespaceop5(self):
        src = u'$a $b+$c $d'
        parser = Parser(src)
        self.assertTrue(parser.match(tokens.START))
        expr = parser.comma_expr()
        expected = NaryOpExpr(
                        op=WhitespaceOp(),
                        operands=[
                            VarName(name=u'a'),
                            BinaryOpExpr(
                                op=AddOp(),
                                lhs=VarName(name=u'b'),
                                rhs=VarName(name=u'c'),
                            ),
                            VarName(name=u'd'),
                        ]
                   )
        self.assertEqual(dump(expected), dump(expr))
        
    def test_naryop(self):
        src = u'$a $b $c, $d $e $f, $g $h $i'
        parser = Parser(src)
        self.assertTrue(parser.match(tokens.START))
        expr = parser.comma_expr()
        expected = NaryOpExpr(
                        op=CommaOp(),
                        operands=[
                            NaryOpExpr(
                                op=WhitespaceOp(),
                                operands=[
                                    VarName(name=u'a'),
                                    VarName(name=u'b'),
                                    VarName(name=u'c'),
                                ]
                            ),
                            NaryOpExpr(
                                op=WhitespaceOp(),
                                operands=[
                                    VarName(name=u'd'),
                                    VarName(name=u'e'),
                                    VarName(name=u'f'),
                                ]
                            ),
                            NaryOpExpr(
                                op=WhitespaceOp(),
                                operands=[
                                    VarName(name=u'g'),
                                    VarName(name=u'h'),
                                    VarName(name=u'i'),
                                ]
                            ),
                        ]
                   )
        self.assertEqual(dump(expected), dump(expr))


#==============================================================================#
class CommaExpression_DivisionOp_TestCase(base.TestCaseBase):
    def test_fwdslash_op1(self):
        src = u'3/2'
        parser = Parser(src)
        self.assertTrue(parser.match(tokens.START))
        expr = parser.comma_expr()
        expected = BinaryOpExpr(
                        op=FwdSlashOp(),
                        lhs=NumberNode(number=u'3'),
                        rhs=NumberNode(number=u'2'),
                   )
        self.assertEqual(dump(expected), dump(expr))
    
    def test_fwdslash_op2(self):
        src = u'-3/2'
        parser = Parser(src)
        self.assertTrue(parser.match(tokens.START))
        expr = parser.comma_expr()
        expected = BinaryOpExpr(
                        op=FwdSlashOp(),
                        lhs=UnaryOpExpr(
                            op=UMinus(),
                            operand=NumberNode(number=u'3'),
                        ),
                        rhs=NumberNode(number=u'2'),
                   )
        self.assertEqual(dump(expected), dump(expr))
    
    def test_fwdslash_op3(self):
        src = u'(-3)/2'
        parser = Parser(src)
        self.assertTrue(parser.match(tokens.START))
        expr = parser.comma_expr()
        expected = BinaryOpExpr(
                        op=FwdSlashOp(),
                        lhs=UnaryOpExpr(
                            op=UMinus(),
                            operand=NumberNode(number=u'3'),
                        ),
                        rhs=NumberNode(number=u'2'),
                   )
        self.assertEqual(dump(expected), dump(expr))
    
    def test_division_op1(self):
        src = u'3/2/1'
        parser = Parser(src)
        self.assertTrue(parser.match(tokens.START))
        expr = parser.comma_expr()
        expected = BinaryOpExpr(
                        op=DivisionOp(),
                        lhs=BinaryOpExpr(
                            op=DivisionOp(),
                            lhs=NumberNode(number=u'3'),
                            rhs=NumberNode(number=u'2'),
                        ),
                        rhs=NumberNode(number=u'1'),
                   )
        self.assertEqual(dump(expected), dump(expr))
    
    def test_division_op2(self):
        src = u'3/-(2/1)'
        parser = Parser(src)
        self.assertTrue(parser.match(tokens.START))
        expr = parser.comma_expr()
        expected = BinaryOpExpr(
                        op=DivisionOp(),
                        lhs=NumberNode(number=u'3'),
                        rhs=UnaryOpExpr(
                            op=UMinus(),
                            operand=BinaryOpExpr(
                                op=DivisionOp(),
                                lhs=NumberNode(number=u'2'),
                                rhs=NumberNode(number=u'1'),
                            )
                        )
                   )
        self.assertEqual(dump(expected), dump(expr))
    
    def test_division_op3(self):
        src = u'-(3/2)/1'
        parser = Parser(src)
        self.assertTrue(parser.match(tokens.START))
        expr = parser.comma_expr()
        expected = BinaryOpExpr(
                        op=DivisionOp(),
                        lhs=UnaryOpExpr(
                            op=UMinus(),
                            operand=BinaryOpExpr(
                                op=DivisionOp(),
                                lhs=NumberNode(number=u'3'),
                                rhs=NumberNode(number=u'2'),
                            )
                        ),
                        rhs=NumberNode(number=u'1'),
                   )
        self.assertEqual(dump(expected), dump(expr))
    
    def test_fwdslash_op4(self):
        src = u'3/$a'
        parser = Parser(src)
        self.assertTrue(parser.match(tokens.START))
        expr = parser.comma_expr()
        expected = BinaryOpExpr(
                        op=DivisionOp(),
                        lhs=NumberNode(number=u'3'),
                        rhs=VarName(name=u'a'),
                   )
        self.assertEqual(dump(expected), dump(expr))
        

#==============================================================================#
class AttribSelector_TestCase(base.TestCaseBase):
    def test_noargs(self):
        src = u'[ abc ]'
        parser = Parser(src)
        self.assertTrue(parser.match(tokens.START))
        sel = parser.attrib_selector()
        expected = "AttributeSelector(attr=u'abc', op=None, val=None)"
        self.assertEqual(expected, dump(sel))
    
    def test_exact_match(self):
        src = u'[ abc="xyz" ]'
        parser = Parser(src)
        self.assertTrue(parser.match(tokens.START))
        sel = parser.attrib_selector()
        expected = "AttributeSelector(attr=u'abc', op=AttrExactMatchOp(), val=StringNode(string=u'xyz'))"
        self.assertEqual(expected, dump(sel))
    
    def test_suffix_match(self):
        src = u'[ abc$=xyz ]'
        parser = Parser(src)
        self.assertTrue(parser.match(tokens.START))
        sel = parser.attrib_selector()
        expected = "AttributeSelector(attr=u'abc', op=AttrSuffixMatchOp(), val=IdentExpr(name=u'xyz'))"
        self.assertEqual(expected, dump(sel))
        

#==============================================================================#
class Selector_TestCase(base.TestCaseBase):
    def test_type_selector(self):
        src = u'div'
        parser = Parser(src)
        self.assertTrue(parser.match(tokens.START))
        sel = parser.selector()
        expected = \
            Selector(
                children=[
                    SimpleSelectorSequence(
                        head=TypeSelector(name=u'div'),
                        tail=[]
                    ),
                ]
            )
        self.assertEqual(dump(expected), dump(sel))
        
    def test_id_selector(self):
        src = u'#myid'
        parser = Parser(src)
        self.assertTrue(parser.match(tokens.START))
        sel = parser.selector()
        expected = \
            Selector(
                children=[
                    SimpleSelectorSequence(
                        head=None,
                        tail=[IdSelector(name=u'myid')]
                    ),
                ]
            )
        self.assertEqual(dump(expected), dump(sel))
        
    def test_class_selector(self):
        src = u'.myclass'
        parser = Parser(src)
        self.assertTrue(parser.match(tokens.START))
        sel = parser.selector()
        expected = \
            Selector(
                children=[
                    SimpleSelectorSequence(
                        head=None,
                        tail=[ClassSelector(name=u'myclass')]
                    ),
                ]
            )
        self.assertEqual(dump(expected), dump(sel))
    
    def test_whitespace_combinator1(self):
        src = u'a b'
        parser = Parser(src)
        self.assertTrue(parser.match(tokens.START))
        sel = parser.selector()
        expected = \
            Selector(
                children=[
                    SimpleSelectorSequence(
                        head=TypeSelector(name=u'a'),
                        tail=[]
                    ),
                    DescendantCombinator(),
                    SimpleSelectorSequence(
                        head=TypeSelector(name=u'b'),
                        tail=[]
                    ),
                ]
            )
        self.assertEqual(dump(expected), dump(sel))
    
    def test_whitespace_combinator2(self):
        src = u'a.myclass b#myid'
        parser = Parser(src)
        self.assertTrue(parser.match(tokens.START))
        sel = parser.selector()
        expected = \
            Selector(
                children=[
                    SimpleSelectorSequence(
                        head=TypeSelector(name=u'a'),
                        tail=[ClassSelector(name=u'myclass')]
                    ),
                    DescendantCombinator(),
                    SimpleSelectorSequence(
                        head=TypeSelector(name=u'b'),
                        tail=[IdSelector(name=u'myid')]
                    ),
                ]
            )
        self.assertEqual(dump(expected), dump(sel))
    
    def test_child_combinator(self):
        src = u'a > b'
        parser = Parser(src)
        self.assertTrue(parser.match(tokens.START))
        sel = parser.selector()
        expected = \
            Selector(
                children=[
                    SimpleSelectorSequence(
                        head=TypeSelector(name=u'a'),
                        tail=[]
                    ),
                    ChildCombinator(),
                    SimpleSelectorSequence(
                        head=TypeSelector(name=u'b'),
                        tail=[]
                    ),
                ]
            )
        self.assertEqual(dump(expected), dump(sel))
    
    def test_pseudo_class_selector1(self):
        src = u'a:link'
        parser = Parser(src)
        self.assertTrue(parser.match(tokens.START))
        sel = parser.selector()
        expected = \
            Selector(
                children=[
                    SimpleSelectorSequence(
                        head=TypeSelector(name=u'a'),
                        tail=[
                            PseudoClassSelector(
                                node=Ident(name=u'link')
                            ),
                        ]
                    )
                ]
            )
        self.assertEqual(dump(expected), dump(sel))
    
    def test_compataibility_pseudo_element_selector(self):
        src = u'a:after'
        parser = Parser(src)
        self.assertTrue(parser.match(tokens.START))
        sel = parser.selector()
        expected = \
            Selector(
                children=[
                    SimpleSelectorSequence(
                        head=TypeSelector(name=u'a'),
                        tail=[
                            PseudoElementSelector(
                                node=Ident(name=u'after')
                            ),
                        ]
                    )
                ]
            )
        self.assertEqual(dump(expected), dump(sel))
    
    def test_pseudo_class_selector2(self):
        src = u'a:foo'
        parser = Parser(src)
        self.assertTrue(parser.match(tokens.START))
        sel = parser.selector()
        expected = \
            Selector(
                children=[
                    SimpleSelectorSequence(
                        head=TypeSelector(name=u'a'),
                        tail=[
                            PseudoClassSelector(
                                node=Ident(name=u'foo')
                            ),
                        ]
                    )
                ]
            )
        self.assertEqual(dump(expected), dump(sel))
    
    def test_pseudo_element_selector2(self):
        src = u'a::foo'
        parser = Parser(src)
        self.assertTrue(parser.match(tokens.START))
        sel = parser.selector()
        expected = \
            Selector(
                children=[
                    SimpleSelectorSequence(
                        head=TypeSelector(name=u'a'),
                        tail=[
                            PseudoElementSelector(
                                node=Ident(name=u'foo')
                            ),
                        ]
                    )
                ]
            )
        self.assertEqual(dump(expected), dump(sel))
    
    def test_negation_selector(self):
        src = u'a:not( #myid )'
        parser = Parser(src)
        self.assertTrue(parser.match(tokens.START))
        sel = parser.selector()
        expected = \
            Selector(
                children=[
                    SimpleSelectorSequence(
                        head=TypeSelector(name=u'a'),
                        tail=[
                            NegationSelector(
                                arg=IdSelector(name=u'myid')
                            ),
                        ]
                    )
                ]
            )
        self.assertEqual(dump(expected), dump(sel))
        

#==============================================================================#


