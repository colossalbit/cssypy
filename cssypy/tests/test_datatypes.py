from cssypy.datatypes import Number, Percentage, Dimension, Color, String, Ident
from cssypy import errors

from . import base


class Number_TestCase(base.TestCaseBase):
    def test_eq(self):
        self.assertTrue(Number(5) == Number(5))
        self.assertTrue(Number(5) == Number(5.0))
        self.assertFalse(Number(7) == Number(12))
        self.assertFalse(Number(5) == 5)
        self.assertFalse(5 == Number(5))
        
    def test_pos(self):
        self.assertEqual(Number(5), +Number(5))
        
    def test_neg(self):
        self.assertEqual(Number(-5), -Number(5))
        
    def test_is_negative(self):
        self.assertEqual(True, (-Number(5)).is_negative())
        self.assertEqual(True,   Number(-5).is_negative())
        self.assertEqual(False,  Number(5).is_negative())
        self.assertEqual(False, (-Number(-5)).is_negative())
        
    def test_sub(self):
        self.assertEqual(Number(5), Number(7)-Number(2))
        with self.assertRaises(TypeError):
            Number(7) - 2
        with self.assertRaises(TypeError):
            7 - Number(2)
    
    def test_mul(self):
        self.assertEqual(Number(15), Number(5)*Number(3))
        with self.assertRaises(TypeError):
            Number(5) * 3
        with self.assertRaises(TypeError):
            5 * Number(3)
    
    def test_div(self):
        self.assertEqual(Number(4), Number(20) / Number(5))
        with self.assertRaises(TypeError):
            Number(20) / 5
        with self.assertRaises(TypeError):
            20 / Number(5)
    
    def test_floordiv(self):
        with self.assertRaises(TypeError):
            Number(20) // Number(5)


class Percentage_TestCase(base.TestCaseBase):
    def test_pos(self):
        self.assertEqual(Percentage(5), +Percentage(5))
        
    def test_neg(self):
        self.assertEqual(Percentage(-5), -Percentage(5))
        
    def test_is_negative(self):
        self.assertEqual(True,  (-Percentage(5)).is_negative())
        self.assertEqual(True,    Percentage(-5).is_negative())
        self.assertEqual(False,   Percentage(5).is_negative())
        self.assertEqual(False, (-Percentage(-5)).is_negative())
            
    def test_eq(self):
        self.assertTrue(Percentage(5) == Percentage(5))
        self.assertTrue(Percentage(5) == Percentage(5.0))
        self.assertTrue(Percentage(5.0) == Percentage(5.0))
        self.assertFalse(Percentage(15) == Percentage(5))
        self.assertFalse(Percentage(5) == 5)
        self.assertFalse(5 == Percentage(5))
        
    def test_add(self):
        self.assertEqual(Percentage(12), Percentage(4) + Percentage(8))
        self.assertEqual(Percentage(12), Percentage(4) + Number(8))
        self.assertEqual(Percentage(12), Number(4) + Percentage(8))
        with self.assertRaises(TypeError):
            Percentage(5) + 100.
        with self.assertRaises(TypeError):
            100. + Percentage(5)
        
    def test_sub(self):
        self.assertEqual(Percentage(18), Percentage(42) - Percentage(24))
        self.assertEqual(Percentage(37.5), Percentage(50) - Number(12.5))
        self.assertEqual(Percentage(37.5), Number(50) - Percentage(12.5))
        with self.assertRaises(TypeError):
            Percentage(50) - 10
        with self.assertRaises(TypeError):
            50 - Percentage(10)


class Dimension_TestCase(base.TestCaseBase):
    def test_pos(self):
        self.assertEqual(Dimension(5,'em'), +Dimension(5,'em'))
        
    def test_neg(self):
        self.assertEqual(Dimension(-5,'em'), -Dimension(5,'em'))
        
    def test_is_negative(self):
        self.assertEqual(True,  (-Dimension(5,'em')).is_negative())
        self.assertEqual(True,    Dimension(-5,'em').is_negative())
        self.assertEqual(False,   Dimension(5,'em').is_negative())
        self.assertEqual(False, (-Dimension(-5,'em')).is_negative())
        
    def test_add(self):
        self.assertEqual(Dimension(5,'em'), Dimension(3,'em')+Number(2))
        self.assertEqual(Dimension(5,'em'), Number(3)+Dimension(2,'em'))
        with self.assertRaises(TypeError):
            Dimension(5, 'em') + 12
        with self.assertRaises(TypeError):
            12 + Dimension(5, 'em')
        
    def test_sub(self):
        self.assertEqual(Dimension(4,'em'), Dimension(6,'em')-Number(2))
        self.assertEqual(Dimension(4,'em'), Number(6)-Dimension(2,'em'))
        with self.assertRaises(errors.CSSTypeError):
            Dimension(5, 'em') - Dimension(6, 'px')
        with self.assertRaises(TypeError):
            Dimension(5, 'em') - 12
        with self.assertRaises(TypeError):
            12 - Dimension(5, 'em')
        
    def test_mul(self):
        self.assertEqual(Dimension(6,'em'), Dimension(3,'em')*Number(2))
        self.assertEqual(Dimension(6,'em'), Number(3)*Dimension(2,'em'))
        with self.assertRaises(TypeError):
            Dimension(5, 'em') * Dimension(12, 'em')
        with self.assertRaises(TypeError):
            Dimension(5, 'em') * 12
        with self.assertRaises(TypeError):
            12 * Dimension(5, 'em')
        
    def test_div(self):
        self.assertEqual(Dimension(5,'em'), Dimension(15,'em')/Number(3))
        self.assertEqual(Dimension(3,'em'), Number(15)/Dimension(5,'em'))
        with self.assertRaises(TypeError):
            Dimension(18, 'em') / Dimension(9, 'em')
        with self.assertRaises(TypeError):
            Dimension(50, 'em') / 10
        with self.assertRaises(TypeError):
            24 / Dimension(6, 'em')
            
    def test_eq(self):
        self.assertTrue(Dimension(4.0,'em') == Dimension(4,'em'))
        self.assertTrue(Dimension(72, 'pt') == Dimension(1,'in'))
        self.assertFalse(Dimension(5, 'em') == Dimension(4,'em'))
        self.assertFalse(Dimension(5, 'em') == Dimension(5,'px'))
        self.assertFalse(Dimension(5, 'em') == Number(4))


class Color_TestCase(base.TestCaseBase):
    def test_eq(self):
        self.assertTrue(Color(rgb=(0,0,0), format='hex') == 
                        Color(rgb=(0,0,0), format='hex'))
        self.assertTrue(Color(rgb=(0,0,0), format='hex') == 
                        Color(rgb=(0.,0.,0.), format='hex'))
        self.assertTrue(Color(hsl=(0,0,0), format='hsl') == 
                        Color(rgb=(0,0,0), format='hex'))
        self.assertFalse(Color(rgb=(0,0,0), format='hex') == 
                         Color(rgb=(1,0,0), format='hex'))
        self.assertFalse(Color(rgb=(0,0,0), format='hex') == 5)

