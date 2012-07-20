import re

from .. import datatypes
from ..utils import stringutil
from .nodes import Node


#==============================================================================#
def _strip_trailing_zeros(s, remove_decimal_point=True):
    """Remove trailing zeros from the string. The string must contain a decimal 
    point. If everything following the decimal point is a zero, the decimal 
    point is also removed.
    """
    if '.' not in s:
        return s
    s = s.rstrip('0')
    if remove_decimal_point and s[-1] == '.':
        s = s[:-1]
    if not s:
        return u'0'
    return s

#==============================================================================#
_datatype_to_node = {}

# Values
class CSSValueNode(Node):
    def to_value(self):
        raise NotImplementedError() # pragma: no cover
        
    def to_css(self, **kwargs):
        raise NotImplementedError() # pragma: no cover
        
    @staticmethod
    def from_value(value):
        assert not value.is_negative()
        cls = _datatype_to_node[type(value)]
        # if value.is_negative():
            # from .expressions import UnaryOpExpr
            # from .operators import UMinus
            # node = cls(-value)
            # return UnaryOpExpr(op=UMinus(), operand=node)
        return cls(value)


#==============================================================================#
re_dimension = re.compile(ur'^(?P<num>[0-9\.]+)(?P<unit>[^0-9\.].*)$')

class DimensionNode(CSSValueNode):
    _fields = ('number', 'unit')
    _precision = 3
    
    def __init__(self, value=None, number=None, unit=None, unescape=True):
        if isinstance(value, basestring):
            assert number is None and unit is None
            m = re_dimension.match(value)
            if not m:
                raise ValueError()
            unit = m.group('unit')
            if unescape:
                unit = stringutil.unescape_identifier(unit)
            self.unit = unit.lower()
            self.number = m.group('num')
        elif isinstance(value, datatypes.Dimension):
            assert number is None and unit is None
            self.unit = value.unit
            n = u'{0:.{p}f}'.format(value.n, p=self._precision)
            self.number = _strip_trailing_zeros(n)
        elif isinstance(number, basestring) and isinstance(unit, basestring):
            assert value is None
            self.number = number
            self.unit = unit
        else:
            raise ValueError()  # TODO
    
    def to_value(self):
        return datatypes.Dimension(float(self.number), self.unit)
        
    def to_css(self):
        return u'{0}{1}'.format(self.number, 
                                stringutil.escape_identifier(self.unit))
        
    def __eq__(self, other):
        if isinstance(other, DimensionNode):
            if self.unit.lower() == other.unit.lower():
                return float(self.number) == float(other.number)
            return False  # TODO: convert to common unit if possible
        return NotImplemented
        
_datatype_to_node[datatypes.Dimension] = DimensionNode

#==============================================================================#
class PercentageNode(CSSValueNode):
    _fields = ('pct',)
    _precision = 1
    
    def __init__(self, value, unescape=True):
        if isinstance(value, basestring):
            if value.endswith('%'):
                value = value[:-1]
            self.pct = value
        elif isinstance(value, datatypes.Percentage):
            pct = u'{0:.{p}f}'.format(value, p=self._precision)
            self.pct = _strip_trailing_zeros(pct)
        else:
            raise ValueError()  # TODO
        
    def to_value(self):
        return datatypes.Percentage(float(self.pct))
            
    def to_css(self):
        return u'{0}%'.format(self.pct)
        
    def __eq__(self, other):
        if isinstance(other, PercentageNode):
            return float(self.pct) == float(other.pct)
        return NotImplemented
        
_datatype_to_node[datatypes.Percentage] = PercentageNode
    
#==============================================================================#
class NumberNode(CSSValueNode):
    _fields = ('number',)
    _precision = 3
    
    def __init__(self, number, unescape=True):
        if isinstance(number, basestring):
            self.number = number
        elif isinstance(number, datatypes.Number):
            n = u'{0:.{p}f}'.format(number, p=self._precision)
            self.number = _strip_trailing_zeros(n)
        else:
            raise ValueError()  # TODO
        
    def to_value(self):
        try:
            return datatypes.Number(int(self.number))
        except ValueError:
            return datatypes.Number(float(self.number))
            
    def to_css(self):
        return u'{0}'.format(self.number)
        
    def __eq__(self, other):
        if isinstance(other, NumberNode):
            # simple string comparison would fail in come cases, e.g.:  7 == 7.0
            return float(self.number) == float(other.number)
        return NotImplemented
        
_datatype_to_node[datatypes.Number] = NumberNode
    
#==============================================================================#
class StringNode(CSSValueNode):
    _fields = ('string',)
    _precision = 3
    
    def __init__(self, string, unescape=True):
        if isinstance(string, basestring):
            self.string = string
            if unescape:
                self.string = stringutil.unquote_string(self.string)
        elif isinstance(string, datatypes.String):
            self.string = str(string)
        else:
            raise ValueError()  # TODO
            
    def to_css(self):
        return stringutil.quote_string(self.string)
    
class UriNode(CSSValueNode):
    pass
    

#==============================================================================#
def _color_to_hex_string(color):
    assert isinstance(color, datatypes.Color)
    r = u'{0:02X}'.format(color.r)
    g = u'{0:02X}'.format(color.g)
    b = u'{0:02X}'.format(color.b)
    if r[0]==r[1] and g[0]==g[1] and b[0]==b[1]:
        return u'{0}{1}{2}'.format(r[0], g[0], b[0])
    else:
        return u'{0}{1}{2}'.format(r, g, b)
        
def _color_to_rgb_string(color):
    assert isinstance(color, datatypes.Color)
    return u'rgb({0},{1},{2})'.format(color.r, color.g, color.b)
        
def _color_to_hsl_string(color):
    assert isinstance(color, datatypes.Color)
    return u'hsl({0},{1},{2})'.format(color.h, color.s, color.l)
    

class ColorNode(CSSValueNode):
    def to_value(self):
        raise NotImplementedError() # pragma: no cover
        
    def to_css_any(self):
        raise NotImplementedError() # pragma: no cover
        
    def to_css_hex(self):
        return _color_to_hex_string(self.to_value())
        
    def to_css_rgb(self):
        return _color_to_rgb_string(self.to_value())
        
    def to_css_hsl(self):
        return _color_to_hsl_string(self.to_value())
        
    def to_css(self, format='any'):
        if format=='any':
            return self.to_css_any()
        if format=='hex':
            return self.to_css_hex()
        elif format=='hsl':
            return self.to_css_hsl()
        elif format=='rgb':
            return self.to_css_rgb()
        else:
            raise RuntimeError()  # TODO
            
    def __eq__(self, other):
        if isinstance(other, ColorNode):
            return self.to_value() == other.to_value()
        return NotImplemented
    
class HexColorNode(ColorNode):
    _fields = ('hex',)
    def __init__(self, hex, unescape=True):
        if isinstance(hex, basestring):
            if hex.startswith('#'):
                hex = hex[1:]
            assert len(hex) == 3 or len(hex) == 6
            self.hex = hex
        elif isinstance(hex, datatypes.Color):
            r = u'{0:02X}'.format(hex.r)
            g = u'{0:02X}'.format(hex.g)
            b = u'{0:02X}'.format(hex.b)
            if r[0]==r[1] and g[0]==g[1] and b[0]==b[1]:
                self.hex = u'{0}{1}{2}'.format(r[0], g[0], b[0])
            else:
                self.hex = u'{0}{1}{2}'.format(r, g, b)
        else:
            raise ValueError()  # TODO
            
    def normalized_hex(self):
        if len(self.hex) == 6:
            r = self.hex[0:2].lower()
            g = self.hex[2:4].lower()
            b = self.hex[4:6].lower()
        else:
            r = (self.hex[0]*2).lower()
            g = (self.hex[1]*2).lower()
            b = (self.hex[2]*2).lower()
        return r,g,b
            
    def to_value(self):
        if len(self.hex) == 3:
            r = int(self.hex[0]*2, 16)
            g = int(self.hex[1]*2, 16)
            b = int(self.hex[2]*2, 16)
        else:
            r = int(self.hex[0:2], 16)
            g = int(self.hex[2:4], 16)
            b = int(self.hex[4:], 16)
        return datatypes.Color(rgb=(r,g,b), format='hex')
            
    def to_css_hex(self):
        return u'#{0}'.format(self.hex)
        
    def to_css_any(self):
        return self.to_css_hex()
        
    def __eq__(self, other):
        if isinstance(other, HexColorNode):
            return self.normalized_hex() == other.normalized_hex()
        return super(HexColorNode, self).__eq__(other)
    
    
def _color_node_factory(value):
    assert isinstance(value, datatypes.Color)
    if value.format == 'hex':
        return HexColorNode(value)
    else:
        raise RuntimeError()

_datatype_to_node[datatypes.Color] = _color_node_factory

#==============================================================================#

__all__ = [ k for k,v in globals().items() 
            if isinstance(v, type) and issubclass(v, Node) and 
               v.__module__ == __name__]


