from __future__ import absolute_import
from __future__ import print_function

from ..utils import stringutil

class Node(object):
    __slots__ = ('lineno', 'filename',)
    _fields = ()
    
    def __init__(self, **kwargs):
        self.lineno = kwargs.pop('lineno', None)
        self.filename = kwargs.pop('filename', '')
        if kwargs:
            msg = "Unexpected keyword arguments: {}"
            msg = msg.format(', '.join("'{}'".format(s) for s in kwargs))
            raise ValueError(msg)
    
    __hash__ = None


class Stylesheet(Node):
    _fields = ('charset', 'imports', 'statements',)
    __slots__ = _fields
    def __init__(self, charset, imports, statements):
        assert all(isinstance(stmt, Statement) for stmt in statements)
        self.charset = charset
        self.imports = imports
        self.statements = statements
        
class ImportedStylesheet(Node):
    _fields = ('imports', 'statements',)
    __slots__ = _fields
    # TODO: this should get lineno from Import node
    def __init__(self, imports, statements, **kwargs):
        super(ImportedStylesheet, self).__init__(**kwargs)
        assert all(isinstance(stmt, Statement) for stmt in statements)
        self.imports = imports
        self.statements = statements
        
class Charset(Node):
    _fields = ('charset',)
    __slots__ = _fields
    def __init__(self, charset, **kwargs):
        super(Charset, self).__init__(**kwargs)
        self.charset = charset
            
    @classmethod
    def from_string(cls, string, **kwargs):
        return cls(charset=stringutil.unquote_string(string), **kwargs)
        
class Import(Node):
    _fields = ('uri',)
    __slots__ = _fields
    # TODO: should this be a statement?
    def __init__(self, uri, **kwargs):
        super(Import, self).__init__(**kwargs)
        self.uri = uri  # UriNode or StringNode
        
class Statement(Node):
    pass
    
class RuleSet(Statement):
    _fields = ('selectors', 'statements',)
    __slots__ = _fields
    def __init__(self, selectors, statements, **kwargs):
        super(RuleSet, self).__init__(**kwargs)
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
    __slots__ = _fields
    def __init__(self, prop, expr, important=False, **kwargs):
        super(Declaration, self).__init__(**kwargs)
        assert expr is None or isinstance(expr, Node)
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
    __slots__ = _fields
    def __init__(self, name, expr, **kwargs):
        super(VarDef, self).__init__(**kwargs)
        assert isinstance(expr, Node)
        self.name = name
        self.expr = expr
            
    @classmethod
    def from_string(cls, string, expr, **kwargs):
        assert string and string[0] == '$'
        return cls(name=stringutil.unescape_identifier(string[1:]), expr=expr, **kwargs)
        
    def __eq__(self, other):
        if isinstance(other, VarDef):
            return (self.name.lower() == other.name.lower() and 
                    self.expr == other.expr)
        return NotImplemented
    
class Property(Node):
    _fields = ('name',)
    __slots__ = _fields
    def __init__(self, name, **kwargs):
        super(Property, self).__init__(**kwargs)
        self.name = name
            
    @classmethod
    def from_string(cls, string, **kwargs):
        return cls(name=stringutil.unescape_identifier(string), **kwargs)
        
    def __eq__(self, other):
        if isinstance(other, Property):
            return self.name.lower() == other.name.lower()
        return NotImplemented

    
class Ident(Node):
    _fields = ('name',)
    __slots__ = _fields
    def __init__(self, name, **kwargs):
        super(Ident, self).__init__(**kwargs)
        self.name = name
            
    @classmethod
    def from_string(cls, string, **kwargs):
        return cls(name=stringutil.unescape_identifier(string), **kwargs)
        
    def __eq__(self, other):
        if isinstance(other, Ident):
            return self.name.lower() == other.name.lower()
        return NotImplemented
        

    
__all__ = [ k for k,v in globals().items() 
            if isinstance(v, type) and issubclass(v, Node) ]

