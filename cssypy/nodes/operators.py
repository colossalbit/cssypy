from __future__ import absolute_import
from __future__ import print_function

from .nodes import Node

PRECEDENCE_UNARY =  6
PRECEDENCE_BINMUL = 4
PRECEDENCE_BINADD = 3
PRECEDENCE_WS =     2
PRECEDENCE_COMMA =  1

#==============================================================================#
class UnaryOperator(Node):
    __slots__ = ()
    _precedence = -1
        
class UMinus(UnaryOperator):
    __slots__ = ()
    _precedence = PRECEDENCE_UNARY
    def __eq__(self, other):
        if isinstance(other, UMinus):
            return True  # all instances are identical
        return NotImplemented
        
    def __str__(self):
        return '-'
        
    def __hash__(self):
        return hash(UMinus)
        
class UPlus(UnaryOperator):
    __slots__ = ()
    _precedence = PRECEDENCE_UNARY
    def __eq__(self, other):
        if isinstance(other, UPlus):
            return True  # all instances are identical
        return NotImplemented
        
    def __str__(self):
        return '+'
        
    def __hash__(self):
        return hash(UPlus)
        
#==============================================================================#
class BinaryOperator(Node):
    __slots__ = ()
    _precedence = -1
    _nary = False
    
class CommaOp(BinaryOperator):
    __slots__ = ()
    _precedence = PRECEDENCE_COMMA
    _nary = True
    def __eq__(self, other):
        if isinstance(other, CommaOp):
            return True  # all instances are identical
        return NotImplemented
        
    def __str__(self):
        return ','
        
    def __hash__(self):
        return hash(CommaOp)
    
class FwdSlashOp(BinaryOperator):
    __slots__ = ()
    _precedence = PRECEDENCE_BINMUL
    def __eq__(self, other):
        if isinstance(other, FwdSlashOp):
            return True  # all instances are identical
        return NotImplemented
        
    def __str__(self):
        return '/'
        
    def __hash__(self):
        return hash(FwdSlashOp)
    
class DivisionOp(BinaryOperator):
    # Used when we know '/' means division
    __slots__ = ()
    _precedence = PRECEDENCE_BINMUL
    def __eq__(self, other):
        if isinstance(other, DivisionOp):
            return True  # all instances are identical
        return NotImplemented
        
    def __str__(self):
        return '/'
        
    def __hash__(self):
        return hash(DivisionOp)
    
class WhitespaceOp(BinaryOperator):
    __slots__ = ()
    _precedence = PRECEDENCE_WS
    _nary = True
    def __eq__(self, other):
        if isinstance(other, WhitespaceOp):
            return True  # all instances are identical
        return NotImplemented
        
    def __str__(self):
        return ' '
        
    def __hash__(self):
        return hash(WhitespaceOp)
    
class AddOp(BinaryOperator):
    __slots__ = ()
    _precedence = PRECEDENCE_BINADD
    def __eq__(self, other):
        if isinstance(other, AddOp):
            return True  # all instances are identical
        return NotImplemented
        
    def __str__(self):
        return '+'
        
    def __hash__(self):
        return hash(AddOp)
    
class SubtractOp(BinaryOperator):
    __slots__ = ()
    _precedence = PRECEDENCE_BINADD
    def __eq__(self, other):
        if isinstance(other, SubtractOp):
            return True  # all instances are identical
        return NotImplemented
        
    def __str__(self):
        return '-'
        
    def __hash__(self):
        return hash(SubtractOp)
    
class MultOp(BinaryOperator):
    __slots__ = ()
    _precedence = PRECEDENCE_BINMUL
    def __eq__(self, other):
        if isinstance(other, MultOp):
            return True  # all instances are identical
        return NotImplemented
        
    def __str__(self):
        return '*'
        
    def __hash__(self):
        return hash(MultOp)
        

#==============================================================================#
# Operators for the AttributeSelector node
class AttributeSelectorOp(Node):
    __slots__ = ()
        
class AttrPrefixMatchOp(AttributeSelectorOp):
    __slots__ = ()
    def __eq__(self, other):
        if isinstance(other, AttrPrefixMatchOp):
            return True  # all instances are identical
        return NotImplemented
        
class AttrSuffixMatchOp(AttributeSelectorOp):
    __slots__ = ()
    def __eq__(self, other):
        if isinstance(other, AttrSuffixMatchOp):
            return True  # all instances are identical
        return NotImplemented
        
class AttrSubstringMatchOp(AttributeSelectorOp):
    __slots__ = ()
    def __eq__(self, other):
        if isinstance(other, AttrSubstringMatchOp):
            return True  # all instances are identical
        return NotImplemented
        
class AttrExactMatchOp(AttributeSelectorOp):
    __slots__ = ()
    def __eq__(self, other):
        if isinstance(other, AttrExactMatchOp):
            return True  # all instances are identical
        return NotImplemented
        
class AttrIncludesMatchOp(AttributeSelectorOp):
    __slots__ = ()
    def __eq__(self, other):
        if isinstance(other, AttrIncludesMatchOp):
            return True  # all instances are identical
        return NotImplemented
        
class AttrDashMatchOp(AttributeSelectorOp):
    __slots__ = ()
    def __eq__(self, other):
        if isinstance(other, AttrDashMatchOp):
            return True  # all instances are identical
        return NotImplemented
        

#==============================================================================#
__all__ = [ k for k,v in globals().items() 
            if isinstance(v, type) and issubclass(v, Node) and 
               v.__module__ == __name__]




