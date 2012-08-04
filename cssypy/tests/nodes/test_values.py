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
        self.assertEqual(u'#AABBCC', HexColorNode(hex=u'AABBCC').to_string(format='hex'))
        self.assertEqual(u'rgb(170,187,204)', HexColorNode(hex=u'AABBCC').to_string(format='rgb'))
        
    def test_to_string_rgb(self):
        self.assertEqual(u'rgb(170,187,204)', HexColorNode(hex=u'AABBCC').to_string_rgb())
        
    def test_to_string_hsl(self):
        self.assertEqual(u'hsl(240,100%,50%)', HexColorNode(hex=u'0000FF').to_string_hsl())


#==============================================================================#
class RGBColorNode_TestCase(base.TestCaseBase):
    def test_to_value(self):
        self.assertEqual(datatypes.Color(rgb=(127,1,51), format='rgb'), 
                         RGBColorNode(r=u'127', g=u'1', b=u'51').to_value())
                         
    def test_from_value(self):
        c = datatypes.Color(rgb=(127,1,51), format='rgb')
        self.assertEqual(RGBColorNode(r=u'127', g=u'1', b=u'51'), RGBColorNode.from_value(c))
        
    def test_to_string(self):
        self.assertEqual(u'rgb(127,1,51)', RGBColorNode(r=u'127', g=u'1', b=u'51').to_string())
        self.assertEqual(u'#7F0133', RGBColorNode(r=u'127', g=u'1', b=u'51').to_string(format='hex'))
        self.assertEqual(u'rgb(127,1,51)', RGBColorNode(r=u'127', g=u'1', b=u'51').to_string(format='rgb'))
        
    def test_to_string_hex(self):
        self.assertEqual(u'#7F0133', RGBColorNode(r=u'127', g=u'1', b=u'51').to_string_hex())
        self.assertEqual(u'#ABC', RGBColorNode(r=u'170', g=u'187', b=u'204').to_string_hex())


#==============================================================================#
class HSLColorNode_TestCase(base.TestCaseBase):
    def test_to_value(self):
        self.assertEqual(datatypes.Color(hsl=(180,0.25,0.50), format='hsl'), 
                         HSLColorNode(h=u'180', s=u'25', l=u'50').to_value())
                         
    def test_from_value(self):
        c = datatypes.Color(hsl=(180,0.25,0.50), format='hsl')
        self.assertEqual(HSLColorNode(h=u'180', s=u'25', l=u'50'), HSLColorNode.from_value(c))
        
    def test_to_string(self):
        self.assertEqual(u'hsl(180,25%,50%)', HSLColorNode(h=u'180', s=u'25', l=u'50').to_string())
        self.assertEqual(u'hsl(180,25%,50%)', HSLColorNode(h=u'180', s=u'25', l=u'50').to_string(format='hsl'))
                         

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
        
    def test_from_value(self):
        self.assertEqual(PercentageNode(pct=u'25'),
                         PercentageNode.from_value(datatypes.Percentage(25)))
                         

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


