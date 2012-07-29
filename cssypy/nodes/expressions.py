from __future__ import absolute_import
from __future__ import print_function

from .nodes import Node, Ident
from .values import CSSValueNode
from ..utils import stringutil
        
class Expr(Node):
    __slots__ = ()

class IdentExpr(Ident, Expr):
    __slots__ = ()
    
class VarName(Expr):
    _fields = ('name',)
    __slots__ = _fields
    def __init__(self, name, **kwargs):
        super(VarName, self).__init__(**kwargs)
        self.name = name
            
    @classmethod
    def from_string(cls, string, **kwargs):
        assert string.startswith(u'$')
        return cls(name=stringutil.unescape_identifier(string[1:]), **kwargs)
        
    def __eq__(self, other):
        if isinstance(other, VarName):
            return self.name.lower() == other.name.lower()
        return NotImplemented
        
    def __str__(self):
        return '${0}'.format(self.name)
        
    def __repr__(self):
        return '<VarName object: {0!r}>'.format('$'+self.name)

class FunctionExpr(Expr):
    _fields = ('name', 'expr')
    __slots__ = _fields
    def __init__(self, name, expr, **kwargs):
        super(FunctionExpr, self).__init__(**kwargs)
        # expr may be None
        self.name = name
        self.expr = expr
            
    @classmethod
    def from_string(cls, string, expr, **kwargs):
        assert string.endswith(u'(')
        return cls(name=stringutil.unescape_identifier(string[:-1]), expr=expr, **kwargs)
        
    def __eq__(self, other):
        if isinstance(other, Function):
            return self.name.lower() == other.name.lower() and self.expr == other.expr
        return NotImplemented
    
class UnaryOpExpr(Expr):
    _fields = ('op', 'operand')
    __slots__ = _fields
    def __init__(self, op, operand, **kwargs):
        super(UnaryOpExpr, self).__init__(**kwargs)
        assert isinstance(operand, (Expr, CSSValueNode))
        self.op = op
        self.operand = operand
        
    def __eq__(self, other):
        if isinstance(other, UnaryOpExpr):
            return self.op == other.op and self.operand == other.operand
        return NotImplemented
        
    def __str__(self):
        return '{0}{1}'.format(self.op, self.operand)
        
    def __repr__(self):
        return '<UnaryOpExpr object: {0!r}>'.format(str(self))
    
class BinaryOpExpr(Expr):
    _fields = ('op', 'lhs', 'rhs')
    __slots__ = _fields
    def __init__(self, op, lhs, rhs, **kwargs):
        super(BinaryOpExpr, self).__init__(**kwargs)
        assert isinstance(lhs, (Expr, CSSValueNode))
        assert isinstance(rhs, (Expr, CSSValueNode))
        self.op = op
        self.lhs = lhs
        self.rhs = rhs
        
    def __eq__(self, other):
        if isinstance(other, BinaryOpExpr):
            return (self.op == other.op and self.lhs == other.lhs and 
                    self.rhs == other.rhs)
        return NotImplemented
        
    def __str__(self):
        return '{1}{0}{2}'.format(self.op, self.lhs, self.rhs)
        
    def __repr__(self):
        return '<BinaryOpExpr object: {0!r}>'.format(str(self))

class NaryOpExpr(Expr):
    _fields = ('op', 'operands')
    __slots__ = _fields
    def __init__(self, op, operand1=None, operand2=None, operands=None, 
                 **kwargs):
        super(NaryOpExpr, self).__init__(**kwargs)
        self.op = op
        if isinstance(operands, (tuple, list)):
            # for testing
            assert operand1 is None
            assert operand2 is None
            self.operands = operands
        else:
            assert operands is None
            assert isinstance(operand1, (Expr, CSSValueNode))
            assert isinstance(operand2, (Expr, CSSValueNode))
            self.operands = [operand1, operand2]
        
    def insert(self, pos, operand):
        assert isinstance(operand, (Expr, CSSValueNode))
        self.operands.insert(pos, operand)
        
    def __eq__(self, other):
        if isinstance(other, NaryOpExpr):
            return self.op == other.op and self.operands == other.operands
        return NotImplemented

    
__all__ = [ k for k,v in globals().items() 
            if isinstance(v, type) and issubclass(v, Node) and 
               v.__module__ == __name__]


