from __future__ import absolute_import
from __future__ import print_function

from .nodes import Node

__all__ = ['iter_fields','iter_child_nodes','walk','debug_tostring','dump',]

def iter_fields(node):
    for name in node._fields:
        yield name, getattr(node, name)
        
def iter_child_nodes(node):
    for name, attr in iter_fields(node):
        if isinstance(attr, (list, tuple)):
            for child in attr:
                if isinstance(child, Node):
                    yield child
        elif isinstance(attr, Node):
            yield attr

def walk(node):
    from collections import deque
    todo = deque([node])
    while todo:
        node = todo.popleft()
        todo.extend(iter_child_nodes(node))
        yield node


def debug_tostring(node, indent=3):     # pragma: no cover
    def attrlist_tostring(name, attr, level):
        pad = ' '*(indent*level)
        head = '{pad}{name}'.format(pad=pad,name='.'+name+':')
        childstrs = []
        for child in attr:
            if isinstance(child, Node):
                s = tostring(child, level+1)
                childstrs.append(s)
            else:
                attrpad = ' '*(indent*(level+1))
                s = '{pad}{0!r}\n'.format(child, pad=attrpad)
                childstrs.append(s)
        return '{0}\n{1}'.format(head, ''.join(childstrs))
        
    def attr_tostring(name, attr, level):
        pad = ' '*(indent*level)
        head = '{pad}{name}'.format(pad=pad,name='.'+name+':')
        s = ''
        if isinstance(attr, Node):
            s = tostring(attr, level+1)
            return '{0}\n{1}'.format(head, s)
        else:
            s = '{0!r}'.format(attr)
            return '{0} {1}\n'.format(head, s)
    
    def tostring(node, level):
        pad = ' '*(indent*level)
        head = '{pad}{name}'.format(pad=pad, name='<'+node.__class__.__name__+'>')
        childstrs = []
        for name, attr in iter_fields(node):
            if isinstance(attr, (list, tuple)):
                s = attrlist_tostring(name, attr, level+1)
                childstrs.append(s)
            elif isinstance(attr, Node):
                s = attr_tostring(name, attr, level+1)
                childstrs.append(s)
            else:
                s = attr_tostring(name, attr, level+1)
                childstrs.append(s)
        if childstrs:
            return '{0}\n{1}'.format(head, ''.join(childstrs))
        else:
            return '{0}\n'.format(head)
    return tostring(node, 0)
    
def dump(node):
    def _format(node):
        if isinstance(node, Node):
            fields = [(a, _format(b)) for a, b in iter_fields(node)]
            rv = '%s(%s' % (node.__class__.__name__, ', '.join(
                ('%s=%s' % field for field in fields)
            ))
            return rv + ')'
        elif isinstance(node, list):
            return '[%s]' % ', '.join(_format(x) for x in node)
        else:
            return repr(node)
    
    if not isinstance(node, Node):
        raise TypeError('expected Node, got %r' % node.__class__.__name__)
    
    return _format(node)


