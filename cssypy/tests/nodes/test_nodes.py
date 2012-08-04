from cssypy.nodes import *
from cssypy import datatypes, errors

from .. import base


#==============================================================================#
class Node_TestCase(base.TestCaseBase):
    def test_unknown_kwargs(self):
        with self.assertRaises(ValueError) as cm:
            Node(unknown_kwarg='abc')
        self.assertTrue(str(cm.exception).startswith("Unexpected keyword arguments:"))
        
#==============================================================================#
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
        
        
#==============================================================================#
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
        

#==============================================================================#

