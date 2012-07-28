from cssypy.nodes import *
from cssypy import datatypes

from .. import base


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
class HexColorNode_TestCase(base.TestCaseBase):
    def test_equal(self):
        self.assertEqual(HexColorNode(hex=u'aabbcc'), HexColorNode(hex=u'aabbcc'))
        self.assertEqual(HexColorNode(hex=u'aabbcc'), HexColorNode(hex=u'abc'))
        self.assertEqual(HexColorNode(hex=u'aabbcc'), HexColorNode(hex=u'AABBCC'))
        self.assertEqual(HexColorNode(hex=u'aabbcc'), HexColorNode(hex=u'ABC'))
        
    def test_to_value(self):
        self.assertEqual(datatypes.Color(rgb=(0xAA,0xBB,0xCC), format='hex'), 
                         HexColorNode(hex=u'AABBCC').to_value())
        self.assertEqual(datatypes.Color(rgb=(0xAA,0xBB,0xCC), format='hex'), 
                         HexColorNode(hex=u'abc').to_value())
                         

#==============================================================================#
class NumberNode_TestCase(base.TestCaseBase):
    def test_equal(self):
        self.assertEqual(NumberNode('11'), NumberNode('11'))
        self.assertEqual(NumberNode('7'), NumberNode('7.0'))
                         

#==============================================================================#
class PercentageNode_TestCase(base.TestCaseBase):
    def test_equal(self):
        self.assertEqual(PercentageNode(pct='25'), PercentageNode(pct='25'))
        self.assertEqual(PercentageNode(pct='46.0'), PercentageNode(pct='46'))
                         

#==============================================================================#
class DimensionNode_TestCase(base.TestCaseBase):
    def test_equal(self):
        self.assertEqual(DimensionNode(number='15', unit='em'), 
                         DimensionNode(number='15', unit='em'))
        self.assertEqual(DimensionNode(number='32', unit='em'), 
                         DimensionNode(number='32.0', unit='em'))
        self.assertFalse(
            DimensionNode(number='32', unit='em') == 
            DimensionNode(number='32.0', unit='px')
        )
        self.assertFalse(DimensionNode(number='32', unit='em') == 5)
        self.assertFalse(5 == DimensionNode(number='32', unit='em'))
        
    def test_from_string(self):
        self.assertEqual( DimensionNode.from_string(u'5em'), DimensionNode(number='5', unit='em'))
        self.assertEqual( DimensionNode.from_string(u'5.em'), DimensionNode(number='5', unit='em'))
        self.assertEqual( DimensionNode.from_string(u'5.0em'), DimensionNode(number='5', unit='em'))
        
        with self.assertRaises(ValueError):
            DimensionNode.from_string(u'em')
        with self.assertRaises(ValueError):
            DimensionNode.from_string(u'5')
                         
                         
#==============================================================================#
class UriNode_TestCase(base.TestCaseBase):
    def test_from_string(self):
        # double quotes
        node = UriNode.from_string(u'url("http://www.example.com/mycss.css")')
        self.assertEqual('http://www.example.com/mycss.css', node.uri)
        # single quotes
        node = UriNode.from_string(u"url('http://www.example.com/mycss.css')")
        self.assertEqual('http://www.example.com/mycss.css', node.uri)
        # no quotes
        node = UriNode.from_string(u'url(http://www.example.com/mycss.css)')
        self.assertEqual('http://www.example.com/mycss.css', node.uri)
        # uppercase
        node = UriNode.from_string(u'URL("http://www.example.com/mycss.css")')
        self.assertEqual('http://www.example.com/mycss.css', node.uri)
        
    def test_to_string(self):
        node = UriNode(uri='http://www.example.com/mycss.css')
        self.assertEqual('url("http://www.example.com/mycss.css")', node.to_string())
        
        
#==============================================================================#

