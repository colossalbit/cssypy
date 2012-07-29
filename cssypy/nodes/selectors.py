from __future__ import absolute_import
from __future__ import print_function

from .nodes import Node
from ..utils import stringutil

#==============================================================================#
class Selector(Node):
    _fields = ('children',)
    __slots__ = _fields
    def __init__(self, children, **kwargs):
        super(Selector, self).__init__(**kwargs)
        if isinstance(children, SimpleSelectorSequence):
            self.children = [children]
        elif isinstance(children, (tuple, list)):
            assert all(isinstance(x, (SimpleSelectorSequence, Combinator)) for x in children), ', '.join(str(type(x)) for x in children)
            self.children = list(children)
        else:
            raise TypeError()
    
    def add_simple_selector_sequence(self, combinator, ssseq):
        assert isinstance(combinator, Combinator)
        assert isinstance(ssseq, SimpleSelectorSequence)
        self.children.extend([combinator, ssseq])
        
    def __eq__(self, other):
        if isinstance(other, Selector):
            return self.children == other.children
        return NotImplemented
        
class SimpleSelectorSequence(Node):
    _fields = ('head', 'tail',)
    __slots__ = _fields
    # head can contain: TypeSelector, UniversalSelector, CombineAncestorSelector
    # tail can contain: IdSelector, ClassSelector, PseudoSelector
    def __init__(self, head, tail, **kwargs):
        super(SimpleSelectorSequence, self).__init__(**kwargs)
        assert head is None or isinstance(head, HeadSimpleSelector), '{0}'.format(type(head))
        assert all(isinstance(x, (TailSimpleSelector, type(None))) for x in tail)
        self.head = head
        self.tail = tail
        
    def __eq__(self, other):
        if isinstance(other, SimpleSelectorSequence):
            return self.head == other.head and self.tail == other.tail
        return NotImplemented
    

#==============================================================================#
# Simple Selectors
class SimpleSelector(Node):
    __slots__ = ()
    
class HeadSimpleSelector(SimpleSelector):
    __slots__ = ()
    
class TailSimpleSelector(SimpleSelector):
    __slots__ = ()
    
class IdSelector(TailSimpleSelector):
    _fields = ('name',)
    __slots__ = _fields
    def __init__(self, name, **kwargs):
        super(IdSelector, self).__init__(**kwargs)
        self.name = name
        
    @classmethod
    def from_string(cls, string, **kwargs):
        assert string.startswith(u'#')
        return cls(name=stringutil.unescape_name(string[1:]), **kwargs)
        
    def __eq__(self, other):
        if isinstance(other, IdSelector):
            return self.name == other.name
        return NotImplemented
    
class TypeSelector(HeadSimpleSelector):
    _fields = ('name',)
    __slots__ = _fields
    def __init__(self, name, **kwargs):
        super(TypeSelector, self).__init__(**kwargs)
        self.name = name
        
    @classmethod
    def from_string(cls, string, **kwargs):
        return cls(name=stringutil.unescape_identifier(string), **kwargs)
        
    def __eq__(self, other):
        if isinstance(other, TypeSelector):
            return self.name == other.name
        return NotImplemented
    
class UniversalSelector(HeadSimpleSelector):
    __slots__ = ()
    def __eq__(self, other):
        if isinstance(other, UniversalSelector):
            return True  # all instances are identical
        return NotImplemented
    
class CombineAncestorSelector(HeadSimpleSelector):
    __slots__ = ()
    def __eq__(self, other):
        if isinstance(other, CombineAncestorSelector):
            return True  # all instances are identical
        return NotImplemented
    
class ClassSelector(TailSimpleSelector):
    _fields = ('name',)
    __slots__ = _fields
    def __init__(self, name, **kwargs):
        super(ClassSelector, self).__init__(**kwargs)
        self.name = name
        
    @classmethod
    def from_string(cls, string, **kwargs):
        return cls(name=stringutil.unescape_identifier(string), **kwargs)
        
    def __eq__(self, other):
        if isinstance(other, ClassSelector):
            return self.name == other.name
        return NotImplemented
    
class PseudoSelector(TailSimpleSelector):
    __slots__ = ()
        
class PseudoClassSelector(PseudoSelector):
    _fields = ('node',)
    __slots__ = _fields
    def __init__(self, node, **kwargs):
        super(PseudoClassSelector, self).__init__(**kwargs)
        # can be a function or an ident
        self.node = node
        
    def __eq__(self, other):
        if isinstance(other, PseudoClassSelector):
            return self.node == other.node
        return NotImplemented
        
class PseudoElementSelector(PseudoSelector):
    _fields = ('node',)
    __slots__ = _fields
    def __init__(self, node, **kwargs):
        super(PseudoElementSelector, self).__init__(**kwargs)
        # can be a function or an ident
        self.node = node
        
    def __eq__(self, other):
        if isinstance(other, PseudoElementSelector):
            return self.node == other.node
        return NotImplemented
        
class NegationSelector(TailSimpleSelector):
    _fields = ('arg',)
    __slots__ = _fields
    def __init__(self, arg, **kwargs):
        super(NegationSelector, self).__init__(**kwargs)
        # can be a function or an ident
        self.arg = arg
        
    def __eq__(self, other):
        if isinstance(other, NegationSelector):
            return self.arg == other.arg
        return NotImplemented
        
class AttributeSelector(TailSimpleSelector):
    _fields = ('attr', 'op', 'val')
    __slots__ = _fields
    def __init__(self, attr, op=None, val=None, **kwargs):
        super(AttributeSelector, self).__init__(**kwargs)
        assert (op is None and val is None) or (op is not None and val is not None)
        self.attr = attr
        self.op = op
        self.val = val # IdentExpr or StringNode
        
    @classmethod
    def from_string(cls, string, op=None, val=None, **kwargs):
        return cls(attr=stringutil.unescape_identifier(string), op=op, val=val, **kwargs)
        
    def __eq__(self, other):
        if isinstance(other, NegationSelector):
            return self.arg == other.arg
        return NotImplemented
    

#==============================================================================#
# Combinators
class Combinator(Node):
    __slots__ = ()
    
class AdjacentSiblingCombinator(Combinator):
    __slots__ = ()
    def __eq__(self, other):
        if isinstance(other, AdjacentSiblingCombinator):
            return True  # all instances are identical
        return NotImplemented
    
class ChildCombinator(Combinator):
    __slots__ = ()
    def __eq__(self, other):
        if isinstance(other, ChildCombinator):
            return True  # all instances are identical
        return NotImplemented
    
class GeneralSiblingCombinator(Combinator):
    __slots__ = ()
    def __eq__(self, other):
        if isinstance(other, GeneralSiblingCombinator):
            return True  # all instances are identical
        return NotImplemented
    
class DescendantCombinator(Combinator):
    __slots__ = ()
    def __eq__(self, other):
        if isinstance(other, DescendantCombinator):
            return True  # all instances are identical
        return NotImplemented


#==============================================================================#
__all__ = [ k for k,v in globals().items() 
            if isinstance(v, type) and issubclass(v, Node) and 
               v.__module__ == __name__]


