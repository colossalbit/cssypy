from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import colorsys


# H: 0..360
# S: 0..1
# L: 0..1

def hsl_to_rgb(h,s,l):
    r,g,b = colorsys.hls_to_rgb(h/360.,l,s)
    return r*255, g*255, b*255

def hsla_to_rgba(h,s,l,a):
    r,g,b = colorsys.hls_to_rgb(h/360.,l,s)
    return r*255, g*255, b*255, a


def rgb_to_hsl(r,g,b):
    h,l,s = colorsys.rgb_to_hls(r/255., g/255., b/255.)
    return h*360., s, l

def rgba_to_hsla(r,g,b,a):
    h,l,s = colorsys.rgb_to_hls(r/255., g/255., b/255.)
    return h*360., s, l, a
