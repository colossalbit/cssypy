from __future__ import absolute_import
from __future__ import print_function

import operator
import itertools

from .base import NodeTransformer
from .. import nodes, errors

ifilter = itertools.ifilter

#==============================================================================#
class ScopeContext(object):
    def __init__(self, solver):
        self.solver = solver
        
    def __enter__(self):
        self.solver.push_scope()
        return self
        
    def __exit__(self, exc_type, exc_value, tb):
        self.solver.pop_scope()
        
        
class NamespaceContext(object):
    def __init__(self, solver):
        self.solver = solver
    
    def __enter__(self):
        self.solver.push_namespace()
        return self
        
    def __exit__(self, exc_type, exc_value, tb):
        self.solver.pop_namespace()
        

class Namespace(object):
    def __init__(self):
        self.scopes = [{}]
        
    def push_scope(self):
        self.scopes.append({})
        
    def pop_scope(self):
        self.scopes.pop()
        
    def merge_child_namespace(self, child):
        assert isinstance(child, Namespace)
        assert len(child.scopes) == 1
        for name, value in child.scopes[0].iteritems():
            if name not in self.scopes[-1]:
                self.scopes[-1][name] = value
        
    def __getitem__(self, name):
        for scope in self.scopes[::-1]:
            try:
                return scope[name]
            except KeyError:
                pass
        # TODO: should this raise an exception or return a sentinel value?
        raise KeyError('name not found')
        
    def __setitem__(self, name, value):
        self.scopes[-1][name] = value


#==============================================================================#
class Solver(NodeTransformer):
    def __init__(self, options=None):
        self.namespaces = []
        self.context = None
        
    def namespace(self):
        return NamespaceContext(self)
        
    def push_namespace(self):
        self.namespaces.append(Namespace())
        
    def pop_namespace(self):
        if len(self.namespaces) > 1:
            child = self.namespaces.pop()
            self.namespaces[-1].merge_child_namespaces(child)
        else:
            self.namespaces.pop()
        
    def scope(self):
        return ScopeContext(self)
        
    def push_scope(self):
        self.namespaces[-1].push_scope()
        
    def pop_scope(self):
        self.namespaces[-1].pop_scope()
        
    def assign_variable(self, name, value):
        self.namespaces[-1][name] = value
        
    def retrieve_variable(self, name):
        return self.namespaces[-1][name]
        
    def node_as_value(self, node):
        assert not isinstance(node, (list, tuple))
        if isinstance(node, nodes.Node):
            return node.to_value()
        return node
        
    def value_as_node(self, value):
        assert not isinstance(value, (list, tuple))
        if not isinstance(value, nodes.Node):
            if value.is_negative():
                node = nodes.CSSValueNode.node_from_value(-value)
                return nodes.UnaryOpExpr(op=nodes.UMinus(), operand=node) 
            else:
                return nodes.CSSValueNode.node_from_value(value)
        return value
        
    #==========================================================================#
    def __call__(self, node):
        return self.visit(node)
        
    def visit_Stylesheet(self, node):
        # new namespace
        with self.namespace():
            node.statements = list(ifilter(bool, (self.visit(stmt) for stmt in node.statements)))
        return node
        
    def visit_ImportedStylesheet(self, node):
        # new namespace
        with self.namespace():
            node.statements = list(ifilter(bool, (self.visit(stmt) for stmt in node.statements)))
        return node
        
    def visit_RuleSet(self, node):
        # new scope
        with self.scope():
            node.selectors = list(ifilter(bool, (self.visit(sel) for sel in node.selectors)))
            node.statements = list(ifilter(bool, (self.visit(stmt) for stmt in node.statements)))
        return node
                
    def visit_Declaration(self, node):
        node.property = self.visit(node.property)
        #TODO: set lineno on value node if it doesn't have one
        node.expr = self.value_as_node(self.visit(node.expr))
        return node

    def visit_VarDef(self, node):
        # solve Expr; Assign to variable.
        # The VarDef node is removed from the syntax tree.
        name = node.name
        #TODO: set lineno on value node if it doesn't have one
        value = self.value_as_node(self.visit(node.expr))
        self.assign_variable(name, value)
        return None
        
    def visit_VarName(self, node):
        # TODO: Replace VarRef with appropriate node.
        #       But, for that we need to know context.  e.g. in a selector, a hash becomes an IdSelector -- in a declaration, a hash becomes a HexColor.
        # TODO: handle unknown name errors
        try:
            return self.retrieve_variable(node.name)
        except KeyError:
            raise errors.CSSVarNameError()
        
    def visit_UnaryOpExpr(self, node):
        # TODO: handle TypeError 'bad operand type for ...' exceptions
        operand = self.visit(node.operand)
        if isinstance(node.op, nodes.UMinus):
            return operator.neg(self.node_as_value(operand))
        elif isinstance(node.op, nodes.UPlus):
            return operator.pos(self.node_as_value(operand))
        else:
            raise RuntimeError()  # pragma: no cover
            
    _binop_map = {
        nodes.AddOp(): operator.add,
        nodes.MultOp(): operator.mul,
        nodes.SubtractOp(): operator.sub,
        nodes.DivisionOp(): operator.truediv,
    }
        
    def visit_BinaryOpExpr(self, node):
        # TODO: handle TypeError 'unsupported operand type ...' exceptions
        lhs = self.visit(node.lhs)
        rhs = self.visit(node.rhs)
        if isinstance(node.op, nodes.FwdSlashOp):
            return node
        try:
            return self._binop_map[node.op](self.node_as_value(lhs), self.node_as_value(rhs))
        except KeyError:
            raise RuntimeError()  # pragma: no cover
        
    def visit_NaryOpExpr(self, node):
        ##node.operands = [self.value_as_node(self.visit(operand)) for operand in node.operands]
        node.operands = list(ifilter(bool, (self.visit(operand) for operand in node.operands)))
        return node
        
    def visit_Function(self, node):
        # TODO: certain functions are handled specially:
        #   rgb(), hsl(), rgba(), hsla() become Colors
        node.expr = self.visit(node.expr)
        return node


#==============================================================================#

