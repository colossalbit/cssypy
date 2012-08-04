from .base import register_builtin
from .. import errors, datatypes

def _rgb_arg(x):
    if isinstance(x, datatypes.Percentage):
        return 255. * x.p / 100.
    elif isinstance(x, datatypes.Number):
        return x.n
    else:
        raise errors.CSSValueError()

@register_builtin
def rgb(r, g, b):
    rgb = tuple(_rgb_arg(x) for x in (r,g,b))
    return datatypes.Color(rgb=rgb, format='rgb')
    

@register_builtin
def hsl(h, s, l):
    if not isinstance(h, datatypes.Number):
        raise errors.CSSValueError()
    h = (h.n % 360. + 360.) % 360.
    if not isinstance(s, datatypes.Percentage) or not isinstance(l, datatypes.Percentage):
        raise errors.CSSValueError()
    s = s.p / 100.
    l = l.p / 100.
    return datatypes.Color(hsl=(h,s,l), format='hsl')
    
