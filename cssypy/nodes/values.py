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
    s = s.rstrip(u'0')
    if remove_decimal_point and s[-1] == u'.':
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
        
    @staticmethod
    def node_from_value(value):
        assert not value.is_negative()
        ValueClass = _datatype_to_node[type(value)]
        return ValueClass.from_value(value)
        
    @classmethod
    def from_value(cls, value):
        raise NotImplementedError() # pragma: no cover
        
    def to_css(self, **kwargs):
        # delete me; deprecated
        raise NotImplementedError() # pragma: no cover
        
    def to_string(self, **kwargs):
        raise NotImplementedError() # pragma: no cover
        
    @classmethod
    def from_string(cls, string):
        raise NotImplementedError() # pragma: no cover


#==============================================================================#
re_dimension = re.compile(ur'^(?P<num>[0-9\.]+)(?P<unit>[^0-9\.].*)$')

class DimensionNode(CSSValueNode):
    _fields = ('number', 'unit')
    _precision = 3
    
    def __init__(self, number=None, unit=None):
        assert isinstance(number, basestring) and isinstance(unit, basestring)
        self.number = number
        self.unit = unit
    
    def to_value(self):
        return datatypes.Dimension(float(self.number), self.unit)
        
    @classmethod
    def from_value(cls, value):
        n = u'{0:.{p}f}'.format(value.n, p=cls._precision)
        return cls(number=_strip_trailing_zeros(n), unit=value.unit)
        
    def to_string(self):
        return u'{0}{1}'.format(self.number, 
                                stringutil.escape_identifier(self.unit))
        
    @classmethod
    def from_string(cls, string):
        m = re_dimension.match(string)
        if not m:
            raise ValueError()  # TODO
        number = m.group('num')
        unit = stringutil.unescape_identifier(m.group('unit'))
        return cls(number=number, unit=unit)
        
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
    
    def __init__(self, pct):
        assert isinstance(pct, basestring)
        self.pct = pct
        
    def to_value(self):
        return datatypes.Percentage(float(self.pct))
        
    @classmethod
    def from_value(cls, value):
        pct = u'{0:.{p}f}'.format(value, p=cls._precision)
        return cls(pct=_strip_trailing_zeros(pct))
            
    def to_string(self):
        return u'{0}%'.format(self.pct)
        
    @classmethod
    def from_string(cls, string):
        assert string and string[-1] == u'%'
        return cls(pct=string[:-1])
        
    def __eq__(self, other):
        if isinstance(other, PercentageNode):
            return float(self.pct) == float(other.pct)
        return NotImplemented
        
_datatype_to_node[datatypes.Percentage] = PercentageNode
    
#==============================================================================#
class NumberNode(CSSValueNode):
    _fields = ('number',)
    _precision = 3
    
    def __init__(self, number):
        assert isinstance(number, basestring)
        self.number = number
        
    def to_value(self):
        try:
            return datatypes.Number(int(self.number))
        except ValueError:
            return datatypes.Number(float(self.number))
        
    @classmethod
    def from_value(cls, value):
        n = u'{0:.{p}f}'.format(value, p=cls._precision)
        return cls(number=_strip_trailing_zeros(n))
            
    def to_string(self):
        return u'{0}'.format(self.number)
        
    @classmethod
    def from_string(cls, string):
        return cls(number=string)
        
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
    
    def __init__(self, string):
        assert isinstance(string, basestring)
        self.string = string
        
    def to_value(self):
        raise NotImplementedError() # TODO
        
    def from_value(cls, value):
        return cls(string=unicode(value))
            
    def to_string(self):
        return stringutil.quote_string(self.string)
        
    @classmethod
    def from_string(cls, string):
        return cls(string=stringutil.unquote_string(string))
        

class UriNode(CSSValueNode):
    _fields = ('uri',)
    
    w = r'(?:[ \t\r\n\f]*)'
    string1 = r'(?:"(?:[^"\\\r\n]|\\[^\r\n])*")'
    string2 = r"(?:'(?:[^'\\\r\n]|\\[^\r\n])*')"
    string = r'(?P<string>{string1}|{string2})'.format(string1=string1, string2=string2)
    bareuri = r'(?P<bareuri>(?:[^"\'\\\r\n\t \(\)]|\\[^\r\n])+)'
    uri = r'[Uu][Rr][Ll]\({w}(?:{string}|{bareuri}){w}\)'.format(w=w, string=string, bareuri=bareuri)
    re_uri = re.compile(uri, re.UNICODE)
    
    def __init__(self, uri):
        self.uri = uri
        
    def to_value(self):
        raise NotImplementedError() # TODO
        
    def from_value(cls, value):
        raise NotImplementedError() # TODO
        
    def to_string(self):
        return u'url({})'.format(stringutil.quote_string(self.uri))
        
    @classmethod
    def from_string(cls, string):
        m = cls.re_uri.match(string)
        if not m:
            raise ValueError()
        s = m.group('string')
        if s:
            return cls(uri=stringutil.unquote_string(s))
        s = m.group('bareuri')
        if s:
            return cls(uri=stringutil.unescape_name(s))
        raise ValueError()
    

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
        
    @classmethod
    def from_value(cls, value):
        raise NotImplementedError() # TODO
        
    def to_string_any(self):
        raise NotImplementedError() # pragma: no cover
        
    def to_string_hex(self):
        return _color_to_hex_string(self.to_value())
        
    def to_string_rgb(self):
        return _color_to_rgb_string(self.to_value())
        
    def to_string_hsl(self):
        return _color_to_hsl_string(self.to_value())
        
    def to_string(self, format='any'):
        if format=='any':
            return self.to_string_any()
        if format=='hex':
            return self.to_string_hex()
        elif format=='hsl':
            return self.to_string_hsl()
        elif format=='rgb':
            return self.to_string_rgb()
        else:
            raise RuntimeError()  # TODO
        
    @classmethod
    def from_string(cls, string):
        raise NotImplementedError() # TODO
            
    def __eq__(self, other):
        if isinstance(other, ColorNode):
            return self.to_value() == other.to_value()
        return NotImplemented
    
class HexColorNode(ColorNode):
    _fields = ('hex',)
    def __init__(self, hex):
        assert isinstance(hex, basestring)
        assert len(hex) == 3 or len(hex) == 6
        self.hex = hex
        # if isinstance(hex, basestring):
            # if hex.startswith('#'):
                # hex = hex[1:]
            # assert len(hex) == 3 or len(hex) == 6
            # self.hex = hex
        # elif isinstance(hex, datatypes.Color):
            # r = u'{0:02X}'.format(hex.r)
            # g = u'{0:02X}'.format(hex.g)
            # b = u'{0:02X}'.format(hex.b)
            # if r[0]==r[1] and g[0]==g[1] and b[0]==b[1]:
                # self.hex = u'{0}{1}{2}'.format(r[0], g[0], b[0])
            # else:
                # self.hex = u'{0}{1}{2}'.format(r, g, b)
        # else:
            # raise ValueError()  # TODO
            
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
        
    @classmethod
    def from_value(cls, value):
        raise NotImplementedError() # TODO
            
    def to_string_hex(self):
        return u'#{0}'.format(self.hex)
        
    def to_string_any(self):
        return self.to_string_hex()
        
    @classmethod
    def from_string(cls, string):
        assert string.startswith(u'#')
        assert len(string) == 4 or len(string) == 7 # '#' + hex chars
        return cls(hex=string[1:])
        
    def __eq__(self, other):
        if isinstance(other, HexColorNode):
            return self.normalized_hex() == other.normalized_hex()
        return super(HexColorNode, self).__eq__(other)
    
    
def _color_node_factory(value):
    assert isinstance(value, datatypes.Color)
    if value.format == 'hex':
        return HexColorNode.from_value(value)
    else:
        raise RuntimeError()

_datatype_to_node[datatypes.Color] = _color_node_factory

#==============================================================================#

__all__ = [ k for k,v in globals().items() 
            if isinstance(v, type) and issubclass(v, Node) and 
               v.__module__ == __name__]


