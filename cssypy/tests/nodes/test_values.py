from cssypy.nodes import *
from cssypy import datatypes, errors

from .. import base

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
                         
    def test_from_value(self):
        c = datatypes.Color(rgb=(0xAA,0xBB,0xCC), format='hex')
        self.assertEqual(HexColorNode(hex=u'AABBCC'), HexColorNode.from_value(c))
        c = datatypes.Color(rgb=(0xAA,0xBB,0xCC), format='hex')
        self.assertEqual(HexColorNode(hex=u'abc'), HexColorNode.from_value(c))
        
    def test_to_string(self):
        self.assertEqual(u'#AABBCC', HexColorNode(hex=u'AABBCC').to_string())
        self.assertEqual(u'#ABC', HexColorNode(hex=u'ABC').to_string())
        self.assertEqual(u'#AABBC0', HexColorNode(hex=u'AABBC0').to_string())


#==============================================================================#
class RGBColorNode_TestCase(base.TestCaseBase):
    def test_to_value(self):
        self.assertEqual(datatypes.Color(rgb=(127,1,51), format='rgb'), 
                         RGBColorNode(r=u'127', g=u'1', b=u'51').to_value())
                         
    def test_from_value(self):
        c = datatypes.Color(rgb=(127,1,51), format='rgb')
        self.assertEqual(RGBColorNode(r=u'127', g=u'1', b=u'51'), RGBColorNode.from_value(c))
                         

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


