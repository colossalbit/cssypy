from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import operator
import colorsys

from . import units, errors
from .utils import colorutil


class DataType(object):
    def is_negative(self):
        return False


class Number(DataType):
    # allowed ops:
    #   ADD, SUB, MUL, DIV with Number
    #   UADD, USUB
    #   conversion to int?, float?
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
        
    def __eq__(self, other):
        if isinstance(other, Number):
            return self.n == other.n
        return NotImplemented
        
    def __hash__(self):
        return hash(self.n)
        
    def __repr__(self):
        return 'Number({})'.format(self.n)
    
    
class Percentage(DataType):
    # allowed ops:
    #   ADD, SUB, MUL, DIV with Number
    #   ADD, SUB with Percentage
    #   UADD, USUB
    def __init__(self, value, nodivide_100=False):
        self.p = value
        
    def is_negative(self):
        return self.p < 0
        
    def __format__(self, format_spec):
        return format(self.p, format_spec)
        
    def __neg__(self):
        return Percentage(-self.p)
        
    def __pos__(self):
        return self  # no-op
        
    def __eq__(self, other):
        if isinstance(other, Percentage):
            return self.p == other.p
        return NotImplemented
        
    def __hash__(self):
        return hash(self.p)
        
    def __repr__(self):
        return 'Percentage({})'.format(self.p)
        
    def __add__(self, other):
        if isinstance(other, Percentage):
            return Percentage(self.p + other.p, nodivide_100=True)
        elif isinstance(other, Number):
            return Percentage(self.p + other.n, nodivide_100=True)
        return NotImplemented
        
    def __radd__(self, other):
        if isinstance(other, Number):
            return Percentage(other.n + self.p, nodivide_100=True)
        return NotImplemented
        
    def __sub__(self, other):
        if isinstance(other, Percentage):
            return Percentage(self.p - other.p, nodivide_100=True)
        elif isinstance(other, Number):
            return Percentage(self.p - other.n, nodivide_100=True)
        return NotImplemented
        
    def __rsub__(self, other):
        if isinstance(other, Number):
            return Percentage(other.n - self.p, nodivide_100=True)
        return NotImplemented


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
        # unit must be in lower case
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
            return Dimension(self.n-other.n, self.unit)
        return NotImplemented
        
    def __rsub__(self, other):
        if isinstance(other, Number):
            return Dimension(other.n - self.n, self.unit)
        return NotImplemented
        
    def __mul__(self, other):
        if isinstance(other, Number):
            return Dimension(self.n * other.n, self.unit)
        return NotImplemented
        
    def __rmul__(self, other):
        if isinstance(other, Number):
            return Dimension(other.n * self.n, self.unit)
        return NotImplemented
        
    def __div__(self, other):
        if isinstance(other, Number):
            return Dimension(self.n / other.n, self.unit)
        return NotImplemented
        
    def __rdiv__(self, other):
        if isinstance(other, Number):
            return Dimension(other.n / self.n, self.unit)
        return NotImplemented
        
    def __repr__(self):
        return 'Dimension({}{})'.format(self.n, self.unit)
        
    def __eq__(self, other):
        if isinstance(other, Dimension):
            if self.unit == other.unit:
                return self.n == other.n
            unitset = units.unitset_lookup.get(self.unit)
            if unitset and (other.unit in unitset):
                a = unitset[self.unit].to_common(self.n)
                b = unitset[other.unit].to_common(other.n)
                return a == b
            else:
                # unknown unit or incompatible units
                return False
        return NotImplemented
    
    
class Color(DataType):
    # allowed ops:
    #   ADD, SUB, MUL, DIV with Number
    #   ADD, SUB with Color
    def __init__(self, rgb=None, hsl=None, format=None):
        assert format and format.lower() in (u'hex',u'hsl',u'rgb')
        self.format = format.lower()
        if rgb:
            assert isinstance(rgb, tuple)
            # each component 0..255
            self._rgba = rgb + (255,)
        elif hsl:
            assert isinstance(hsl, tuple)
            # H:   0..360
            # S,L: 0..1
            rgb = colorutil.hsl_to_rgb(*hsl)
            self._rgba = rgb + (255,)
        else:
            raise RuntimeError('TODO')
            
    @property
    def hsla(self):
        return colorutil.rgba_to_hsla(*self._rgba)
        
    @property
    def rgba(self):
        return self._rgba
            
    def __eq__(self, other):
        if isinstance(other, Color):
            return self._rgba == other._rgba
        return NotImplemented
        
        
class String(DataType):
    # strings in non-expression contexts are turned into the appropriate value:
    #   IdSelector, Number, ClassSelector, Ident, PseudoSelector
    def __init__(self, value):
        self.s = value
        
    def __repr__(self):
        return 'String({})'.format(self.s)
        
        
class Ident(DataType):
    # similar to a string, but without quotes
    def __init__(self, value):
        self.name = value
        
    def __repr__(self):
        return 'Ident({})'.format(self.name)



