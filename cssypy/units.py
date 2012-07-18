from math import pi as PI

class UnitSet(object):
    def __init__(self, name, common_unit, entries):
        self.name = name
        self.common_unit = ''
        self.entries = entries
        
    def __contains__(self, unit):
        return unit in self.entries
        
    def __getitem__(self, unit):
        return self.entries[unit]
        
        
class UnitSetEntry(object):
    def __init__(self, unit, conv):
        self.unit = unit
        self.conv = conv
        
    def to_common(self, value):
        return value * self.conv
        
    def from_common(self, value):
        return value / self.conv


_unitsets = (
    ('lengths', ('px', (
        ('px', 1.0),
        ('cm', 37.79527559),    # 1 cm -> 37.79527559 px
        ('mm', 3.779527559),    # 1 mm -> 3.779527559 px
        ('in', 96.),            # 1 in -> 96 px
        ('pt', 4./3.),          # 1 pt -> 1.3333... px
        ('pc', 16.),            # 1 pc -> 16 px
    ))),
    ('angles', ('rad', (
        ('rad',  1.0),
        ('deg',  (2.*PI)/360.),
        ('grad', (2.*PI)/400.),
        ('turn', (2.*PI)/1.),
    ))),
    ('times', ('s', (
        ('s',  1.0),
        ('ms', 1./1000.),
    ))),
    ('ems',   ('em',   (('em',   1.0),))),
    ('exs',   ('ex',   (('ex',   1.0),))),
    ('chs',   ('ch',   (('ch',   1.0),))),
    ('rems',  ('rem',  (('rem',  1.0),))),
    ('vws',   ('vw',   (('vw',   1.0),))),
    ('vhs',   ('vh',   (('vh',   1.0),))),
    ('vmins', ('vmin', (('vmin', 1.0),))),
    ('freqs', ('hz', (
        ('hz',  1.0),
        ('khz', 1000.),
    ))),
    ('resolutions', ('dppx', (
        ('dppx',  1.0),
        ('dpcm', 1./37.79527559),
        ('dpi', 1./96.),
    ))),
)

def _make_unitset(name, unitset):
    common, unitinfos = unitset
    entries = dict((unit, UnitSetEntry(unit, conv)) for unit, conv in unitinfos)
    return UnitSet(name, common, entries)

unitsets = {}
    
for _name, _unitset in _unitsets:
    unitsets[_name] = _make_unitset(_name, _unitset)
    
unitset_lookup = {}

for _unitset in unitsets.itervalues():
    for _unitname in _unitset.entries:
        unitset_lookup[_unitname] = _unitset

