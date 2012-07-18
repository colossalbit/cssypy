from cssypy.nodes import *
from cssypy import datatypes

from .. import base


class RuleSet_TestCase(base.TestCaseBase):
    def test_equal(self):
        a = RuleSet(
                selectors=[
                    Selector(
                        children=[
                            SimpleSelectorSequence(
                                head=TypeSelector(name='div'), 
                                tail=[]
                            )
                        ]
                    )
                ],
                statements=[]
            )
        b = RuleSet(
                selectors=[
                    Selector(
                        children=[
                            SimpleSelectorSequence(
                                head=TypeSelector(name='div'), 
                                tail=[]
                            )
                        ]
                    )
                ],
                statements=[]
            )
        self.assertEqual(a, b)
        
        
class MiscEquality_TestCase(base.TestCaseBase):
    def test_combinators(self):
        self.assertEqual(AdjacentSiblingCombinator(), AdjacentSiblingCombinator())
        self.assertEqual(GeneralSiblingCombinator(), GeneralSiblingCombinator())
        self.assertEqual(ChildCombinator(), ChildCombinator())
        self.assertEqual(DescendantCombinator(), DescendantCombinator())
        
    def test_singleton_selectors(self):
        self.assertEqual(UniversalSelector(), UniversalSelector())
        self.assertEqual(CombineAncestorSelector(), CombineAncestorSelector())
        
    def test_unary_operators(self):
        self.assertEqual(UPlus(), UPlus())
        self.assertEqual(UMinus(), UMinus())
        
    def test_binary_operators(self):
        self.assertEqual(CommaOp(), CommaOp())
        self.assertEqual(FwdSlashOp(), FwdSlashOp())
        self.assertEqual(DivisionOp(), DivisionOp())
        self.assertEqual(WhitespaceOp(), WhitespaceOp())
        self.assertEqual(AddOp(), AddOp())
        self.assertEqual(SubtractOp(), SubtractOp())
        self.assertEqual(MultOp(), MultOp())
        
        
class HexColorNode_TestCase(base.TestCaseBase):
    def test_equal(self):
        self.assertEqual(HexColorNode(hex=u'#aabbcc'), HexColorNode(hex=u'#aabbcc'))
        self.assertEqual(HexColorNode(hex=u'#aabbcc'), HexColorNode(hex=u'#abc'))
        self.assertEqual(HexColorNode(hex=u'#aabbcc'), HexColorNode(hex=u'#AABBCC'))
        self.assertEqual(HexColorNode(hex=u'#aabbcc'), HexColorNode(hex=u'#ABC'))
        
    def test_to_value(self):
        self.assertEqual(datatypes.Color(rgb=(0xAA,0xBB,0xCC), format='hex'), 
                         HexColorNode(hex=u'#AABBCC').to_value())
        self.assertEqual(datatypes.Color(rgb=(0xAA,0xBB,0xCC), format='hex'), 
                         HexColorNode(hex=u'#abc').to_value())
                         

class NumberNode_TestCase(base.TestCaseBase):
    def test_equal(self):
        self.assertEqual(NumberNode('11'), NumberNode('11'))
        self.assertEqual(NumberNode('7'), NumberNode('7.0'))
                         

class PercentageNode_TestCase(base.TestCaseBase):
    def test_equal(self):
        self.assertEqual(PercentageNode('25%'), PercentageNode('25%'))
        self.assertEqual(PercentageNode('46.0%'), PercentageNode('46%'))
                         

class DimensionNode_TestCase(base.TestCaseBase):
    def test_equal(self):
        self.assertEqual(DimensionNode('15em'), DimensionNode('15em'))
        self.assertEqual(DimensionNode('32em'), DimensionNode('32.0em'))
        



