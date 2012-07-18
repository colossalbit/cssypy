from ..utils import escapes

class Node(object):
    __slots__ = ()
    _fields = ()
    
    __hash__ = None


class Stylesheet(Node):
    _fields = ('charset', 'statements',)
    def __init__(self, charset, statements, unescape=True):
        assert all(isinstance(stmt, Statement) for stmt in statements)
        self.charset = charset
        self.statements = statements
        
class Charset(Node):
    _fields = ('charset',)
    def __init__(self, charset, unescape=True):
        self.charset = charset
        if unescape:
            self.charset = escapes.unquote_string(self.charset)
        
class Statement(Node):
    pass
    
class RuleSet(Statement):
    _fields = ('selectors', 'statements',)
    def __init__(self, selectors, statements, unescape=True):
        assert all(isinstance(stmt, Statement) for stmt in statements)
        self.selectors = selectors
        self.statements = statements
        
    def __eq__(self, other):
        if isinstance(other, RuleSet):
            return (self.selectors == other.selectors and 
                    self.statements == other.statements)
        return NotImplemented


class Declaration(Statement):
    _fields = ('property', 'expr', 'important',)
    def __init__(self, prop, expr, important=False, unescape=True):
        ##assert expr is None or isinstance(expr, ExprBase)
        assert isinstance(prop, Property)
        self.property = prop
        self.expr = expr
        self.important = important
        
    def __eq__(self, other):
        if isinstance(other, Declaration):
            return (self.property == other.property and 
                    self.expr == other.expr and 
                    self.important == other.important)
        return NotImplemented
        
        
class VarDef(Statement):
    _fields = ('name', 'expr')
    def __init__(self, name, expr, unescape=True):
        self.name = name
        self.expr = expr
        if unescape:
            self.name = escapes.unescape_identifier(self.name)
        
    def __eq__(self, other):
        if isinstance(other, VarDef):
            return (self.name.lower() == other.name.lower() and 
                    self.expr == other.expr)
        return NotImplemented
    
class Property(Node):
    _fields = ('name',)
    def __init__(self, name, unescape=True):
        self.name = name
        if unescape:
            self.name = escapes.unescape_identifier(self.name)
        
    def __eq__(self, other):
        if isinstance(other, Property):
            return self.name.lower() == other.name.lower()
        return NotImplemented

    
class Ident(Node):
    _fields = ('name',)
    def __init__(self, name, unescape=True):
        self.name = name
        if unescape:
            self.name = escapes.unescape_identifier(self.name)
        
    def __eq__(self, other):
        if isinstance(other, Ident):
            return self.name.lower() == other.name.lower()
        return NotImplemented
        

    
__all__ = [ k for k,v in globals().items() 
            if isinstance(v, type) and issubclass(v, Node) ]

