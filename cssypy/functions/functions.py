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


