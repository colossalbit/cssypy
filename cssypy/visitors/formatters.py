from .base import NodeVisitor
from .. import nodes
from ..utils import stringutil


#==============================================================================#
class CSSFormatterVisitor(NodeVisitor):
    def __init__(self, stream):
        self.indent_str = u' '*4
        self.indent_level = 0
        self.line_width = 80
        self.stream = stream
        self._cache = u''
        self._last_optional_newline = 0
        
    def newline(self):
        self.write(u'\n')
        self.flush()
        self.write(self.indent_str * self.indent_level)
        
    def push_indent(self):
        self.indent_level += 1
        
    def pop_indent(self):
        self.indent_level -= 1
        
    def write(self, data):
        self._cache += data
        if self._last_optional_newline and len(self._cache) > self.line_width:
            temp = self._cache[self._last_optional_newline:]
            self._cache = self._cache[:self._last_optional_newline]
            self.newline()
            self._cache = temp
        ##self.stream.write(data)
        
    def optional_newline(self):
        if len(self._cache) > self.line_width:
            self.newline()
        else:
            self._last_optional_newline = len(self._cache)
        
    def flush(self):
        ##print 'type(self._cache): {0}'.format(type(self._cache))
        self.stream.write(self._cache)
        self._cache = u''
        self._last_optional_newline = 0
        
    def generic_visit(self, node):
        super(CSSFormatterVisitor, self).generic_visit(node)
    
    # Structure...
    def visit_Stylesheet(self, node):
        for stmt in node.statements:
            self.visit(stmt)
            self.newline()
        self.flush()
        
    def visit_RuleSet(self, node):
        # selectors { PUSH_INDENT NL statements POP_INDENT NL }
        for selector in node.selectors[:-1]:
            self.visit_Selector(selector)
            self.write(u', ')
            self.optional_newline()
        self.visit_Selector(node.selectors[-1])
        
        if node.statements:
            self.write(u' {')
            self.push_indent()
            self.newline()
            
            for stmt in node.statements[:-1]:
                self.visit(stmt)
                self.newline()
            self.visit(node.statements[-1])
            
            self.pop_indent()
            self.newline()
            self.write(u'}')
        else:
            self.write(u' {}')
        
    def visit_Declaration(self, node):
        # INDENT property: expression !important?; NL
        self.visit(node.property)
        self.write(u': ')
        self.visit(node.expr)
        if node.important:
            self.write(u' !important')
        self.write(u';')
        
    def visit_Selector(self, node):
        # SSS COMB SSS
        for child in node.children:
            if isinstance(child, nodes.DescendantCombinator):
                self.visit(child)
            elif isinstance(child, nodes.Combinator):
                self.write(u' ')
                self.visit(child)
                self.write(u' ')
            else:
                self.visit(child)
        
    def visit_SimpleSelectorSequence(self, node):
        if node.head:
            self.visit(node.head)
        for child in node.tail:
            self.visit(child)
        
    def visit_Property(self, node):
        self.write(stringutil.escape_identifier(node.name))
        
    def visit_UnaryOpExpr(self, node):
        self.visit(node.op)
        if hasattr(node.operand, 'op'):
            self.write(u'(')
            self.visit(node.operand)
            self.write(u')')
        else:
            self.visit(node.operand)
        
    def visit_BinaryOpExpr(self, node):
        # if priority(lhs) < priority(op): surround w/ parentheses
        if hasattr(node.lhs, 'op') and node.lhs.op._precedence < node.op._precedence:
            self.write(u'(')
            self.visit(node.lhs)
            self.write(u')')
        else:
            self.visit(node.lhs)
        
        self.visit(node.op)
        
        # if priority(rhs) <= priority(op): surround w/ parentheses
        if hasattr(node.rhs, 'op') and node.rhs.op._precedence <= node.op._precedence:
            self.write(u'(')
            self.visit(node.rhs)
            self.write(u')')
        else:
            self.visit(node.rhs)
        
    def visit_NaryOpExpr(self, node):
        if node.operands:
            self.visit(node.operands[0])
            for operand in node.operands[1:]:
                self.visit(node.op)
                self.visit(operand)
        
    # Names...
    def visit_Ident(self, node):
        self.write(stringutil.escape_identifier(node.name))
        
    def visit_IdentExpr(self, node):
        self.write(node.name)
        
    def visit_VarName(self, node):
        self.write(u'$')
        self.write(stringutil.escape_identifier(node.name))
        
    def visit_FunctionExpr(self, node):
        self.write(stringutil.escape_identifier(node.name))
        self.write(u'(')
        self.visit(node.expr)
        self.write(u')')
        
    # Selectors...
    def visit_IdSelector(self, node):
        self.write(u'#')
        self.write(stringutil.escape_name(node.name))
        
    def visit_ClassSelector(self, node):
        self.write(u'.')
        self.write(node.name)
        
    def visit_TypeSelector(self, node):
        self.write(stringutil.escape_identifier(node.name))
        
    def visit_UniversalSelector(self, node):
        self.write(u'*')
        
    def visit_CombineAncestorSelector(self, node):
        self.write(u'&')
        
    def visit_PseudoClassSelector(self, node):
        self.write(u':')
        self.visit(node.node)
        
    def visit_PseudoElementSelector(self, node):
        self.write(u'::')
        self.visit(node.node)
        
    def visit_NegationSelector(self, node):
        self.write(u':not(')
        self.visit(node.arg)
        self.write(u')')
        
    def visit_AttributeSelector(self, node):
        self.write(u'[')
        self.write(stringutil.escape_identifier(node.attr))
        if node.op:
            assert node.val
            self.visit(node.op)
            self.visit(node.val)
        self.write(u']')
        
    # Combinators...
    def visit_DescendantCombinator(self, node):
        self.write(u' ')
        
    def visit_AdjacentSiblingCombinator(self, node):
        self.write(u'+')
        
    def visit_ChildCombinator(self, node):
        self.write(u'>')
        
    def visit_GeneralSiblingCombinator(self, node):
        self.write(u'~')
        
    # Values...
    def visit_DimensionNode(self, node):
        self.write(node.to_css())
        
    def visit_PercentageNode(self, node):
        self.write(node.to_css())
        
    def visit_NumberNode(self, node):
        self.write(node.to_css())
        
    def visit_StringNode(self, node):
        self.write(node.to_css())
        
    def visit_UriNode(self, node):
        self.write(node.to_css())
        
    def visit_ColorNode(self, node):
        self.write(node.value)
        
    def visit_HexColorNode(self, node):
        self.write(node.to_css())
        
    # Operators...
    def visit_UPlus(self, node):
        self.write(u'+')
    
    def visit_UMinus(self, node):
        self.write(u'-')
    
    def visit_CommaOp(self, node):
        self.write(u', ')
    
    def visit_FwdSlashOp(self, node):
        self.write(u'/')
    
    def visit_WhitespaceOp(self, node):
        self.write(u' ')
    
    def visit_AddOp(self, node):
        self.write(u'+')
    
    def visit_SubtractOp(self, node):
        self.write(u'-')
    
    def visit_MultOp(self, node):
        self.write(u'*')
    
    def visit_DivisionOp(self, node):
        self.write(u'/')
        
    # Attribute selector operators...
    def visit_AttrPrefixMatchOp(self, node):
        self.write(u'^=')
        
    def visit_AttrSuffixMatchOp(self, node):
        self.write(u'$=')
        
    def visit_AttrSubstringMatchOp(self, node):
        self.write(u'*=')
        
    def visit_AttrExactMatchOp(self, node):
        self.write(u'=')
        
    def visit_AttrIncludesMatchOp(self, node):
        self.write(u'~=')
        
    def visit_AttrDashMatchOp(self, node):
        self.write(u'|=')


#==============================================================================#

