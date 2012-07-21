from ..utils import stringutil

class Node(object):
    __slots__ = ()
    _fields = ()
    
    __hash__ = None


class Stylesheet(Node):
    _fields = ('charset', 'imports', 'statements',)
    def __init__(self, charset, imports, statements):
        assert all(isinstance(stmt, Statement) for stmt in statements)
        self.charset = charset
        self.imports = imports
        self.statements = statements
        
class ImportedStylesheet(Node):
    _fields = ('imports', 'statements',)
    def __init__(self, imports, statements):
        assert all(isinstance(stmt, Statement) for stmt in statements)
        self.imports = imports
        self.statements = statements
        
class Charset(Node):
    _fields = ('charset',)
    def __init__(self, charset):
        self.charset = charset
            
    @classmethod
    def from_string(cls, string):
        return cls(charset=stringutil.unquote_string(string))
        
class Import(Node):
    _fields = ('uri',)
    def __init__(self, uri):
        self.uri = uri  # UriNode or StringNode
        
class Statement(Node):
    pass
    
class RuleSet(Statement):
    _fields = ('selectors', 'statements',)
    def __init__(self, selectors, statements):
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
    def __init__(self, prop, expr, important=False):
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
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr
            
    @classmethod
    def from_string(cls, string, expr):
        assert string and string[0] == '$'
        return cls(name=stringutil.unescape_identifier(string[1:]), expr=expr)
        
    def __eq__(self, other):
        if isinstance(other, VarDef):
            return (self.name.lower() == other.name.lower() and 
                    self.expr == other.expr)
        return NotImplemented
    
class Property(Node):
    _fields = ('name',)
    def __init__(self, name):
        self.name = name
            
    @classmethod
    def from_string(cls, string):
        return cls(name=stringutil.unescape_identifier(string))
        
    def __eq__(self, other):
        if isinstance(other, Property):
            return self.name.lower() == other.name.lower()
        return NotImplemented

    
class Ident(Node):
    _fields = ('name',)
    def __init__(self, name):
        self.name = name
            
    @classmethod
    def from_string(cls, string):
        return cls(name=stringutil.unescape_identifier(string))
        
    def __eq__(self, other):
        if isinstance(other, Ident):
            return self.name.lower() == other.name.lower()
        return NotImplemented
        

    
__all__ = [ k for k,v in globals().items() 
            if isinstance(v, type) and issubclass(v, Node) ]

