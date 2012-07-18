from __future__ import division
import operator

from . import units, errors


class DataType(object):
    def is_negative(self):
        return False


class Number(DataType):
    # allowed ops:
    #   ADD, SUB, MUL, DIV with Number
    #   UADD, USUB
    def __init__(self, number):
        self.n = number
        
    def is_negative(self):
        return self.n < 0
        
    def __format__(self, format_spec):
        return format(self.n, format_spec)
        
    def __neg__(self):
        return Number(-self.n)
        
    def __pos__(self):
        return self  # no-op
        
    def __add__(self, other):
        if isinstance(other, Number):
            return Number(self.n + other.n)
        return NotImplemented
        
    def __sub__(self, other):
        if isinstance(other, Number):
            return Number(self.n - other.n)
        return NotImplemented
        
    def __mul__(self, other):
        if isinstance(other, Number):
            return Number(self.n * other.n)
        return NotImplemented
        
    def __div__(self, other):
        if isinstance(other, Number):
            return Number(self.n / other.n)
        return NotImplemented
        
    def __truediv__(self, other):
        if isinstance(other, Number):
            return Number(self.n / other.n)
        return NotImplemented
    
    
class Percentage(DataType):
    # allowed ops:
    #   ADD, SUB, MUL, DIV with Number
    #   ADD, SUB with Percentage
    #   UADD, USUB
    def __init__(self, value):
        self.p = value / 100.
        
    def is_negative(self):
        return self.p < 0
        
    def __format__(self, format_spec):
        return format(self.p*100., format_spec)
        
    def __neg__(self):
        return Percentage(-self.p)
        
    def __pos__(self):
        return self  # no-op


def _dimension_op(unitset, op, a, b):
    x1 = unitset[a.unit].to_common(a.n)
    x2 = unitset[b.unit].to_common(b.n)
    x = op(x1, x2)
    n = unitset[a.unit].from_common(x)
    return Dimension(n, a.unit)


class Dimension(DataType):
    # allowed ops:
    #   ADD, SUB, MUL, DIV with Number
    #   ADD, SUB with Dimension (depending on unit)
    #   UADD, USUB
    def __init__(self, number, unit):
        self.n = number
        self.unit = unit
        
    def is_negative(self):
        return self.n < 0
        
    def __neg__(self):
        return Dimension(-self.n, self.unit)
        
    def __pos__(self):
        return self  # no-op
        
    def __add__(self, other):
        if isinstance(other, Dimension):
            if self.unit == other.unit:
                return Dimension(self.n+other.n, self.unit)
            unitset = units.unitset_lookup.get(self.unit)
            if unitset and (other.unit in unitset):
                return _dimension_op(unitset, operator.add, self, other)
            else:
                # unknown unit or incompatible units
                msg = ("Incompatible units. Cannot add Dimension objects "
                       "with '{0}' and '{1}' units.")
                msg = msg.format(self.unit, other.unit)
                raise errors.CSSTypeError(msg)
        elif isinstance(other, Number):
            return Dimension(self.n+other.n, self.unit)
        return NotImplemented
        
    def __radd__(self, other):
        if isinstance(other, Number):
            return Dimension(other.n+self.n, self.unit)
        return NotImplemented
        
    def __sub__(self, other):
        if isinstance(other, Dimension):
            if self.unit == other.unit:
                return Dimension(self.n - other.n, self.unit)
            unitset = units.unitset_lookup.get(self.unit)
            if unitset and (other.unit in unitset):
                return _dimension_op(unitset, operator.sub, self, other)
            else:
                # unknown unit or incompatible units
                msg = ("Incompatible units. Cannot subtract Dimension objects "
                       "with '{0}' and '{1}' units.")
                msg = msg.format(self.unit, other.unit)
                raise errors.CSSTypeError(msg)
        elif isinstance(other, Number):
            return Dimension(self.n+other.n, self.unit)
        return NotImplemented
        
    def __rsub__(self, other):
        if isinstance(other, Number):
            return Dimension(other.n - self.n, self.unit)
        return NotImplemented
    
    
class Color(DataType):
    # allowed ops:
    #   ADD, SUB, MUL, DIV with Number
    #   ADD, SUB with Color
    def __init__(self, rgb=None, hsl=None, format=None):
        assert format.lower() in (u'hex',u'hsl')
        self.format = format.lower()
        if rgb:
            assert isinstance(rgb, tuple)
            self.rgba = rgb + (255,)
        else:
            raise RuntimeError('TODO')
            
    @property
    def r(self):
        return self.rgba[0]
    @property
    def g(self):
        return self.rgba[1]
    @property
    def b(self):
        return self.rgba[2]
    @property
    def a(self):
        return self.rgba[3]
            
    def __eq__(self, other):
        if isinstance(other, Color):
            return self.rgba == other.rgba
        return NotImplemented
        
        
class String(DataType):
    # strings in non-expression contexts are turned into the appropriate value:
    #   IdSelector, Number, ClassSelector, Ident, PseudoSelector
    def __init__(self, value):
        pass
        
        
class Ident(DataType):
    # similar to a string, but without quotes
    def __init__(self, value):
        pass



