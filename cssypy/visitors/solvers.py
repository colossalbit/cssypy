import operator

from .base import NodeTransformer
from .. import nodes


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
        raise RuntimeError('name not found')
        
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
        if isinstance(node, nodes.Node):
            return node.to_value()
        return node
        
    def value_as_node(self, value):
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
            node.statements = [self.visit(stmt) for stmt in node.statements]
        return node
        
    def visit_RuleSet(self, node):
        # new scope
        with self.scope():
            ##with self.selector_context():
            node.selectors = [self.visit(sel) for sel in node.selectors]
            node.statements = [self.visit(stmt) for stmt in node.statements]
        return node
                
    def visit_Declaration(self, node):
        ##with self.declaration_context():
        node.property = self.visit(node.property)
        node.expr = self.value_as_node(self.visit(node.expr))
        return node

    def visit_VarDef(self, node):
        # solve Expr; Assign to variable.
        # The VarDef node is removed from the syntax tree.
        name = node.name
        value = self.visit(node.expr)
        self.assign_variable(name, value)
        return None
        
    def visit_VarRef(self, node):
        # TODO: Replace VarRef with appropriate node.
        #       But, for that we need to know context.  e.g. in a selector, a hash becomes an IdSelector -- in a declaration, a hash becomes a HexColor.
        return node
        
    def visit_Expr(self, node):
        # TODO: Compute arithmetic and function calls
        return node
        
    def visit_UnaryOpExpr(self, node):
        # TODO: handle TypeError 'bad operand type for ...' exceptions
        operand = self.visit(node.operand)
        if isinstance(node.op, nodes.UMinus):
            return operator.neg(self.node_as_value(operand))
        elif isinstance(node.op, nodes.UPlus):
            return operator.pos(self.node_as_value(operand))
        else:
            raise RuntimeError()  # TODO
            
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
            raise RuntimeError()  # TODO
        # elif isinstance(node.op, nodes.AddOp):
            # return self.node_as_value(lhs) + self.node_as_value(rhs)
        # elif isinstance(node.op, nodes.MultOp):
            # return self.node_as_value(lhs) * self.node_as_value(rhs)
        # elif isinstance(node.op, nodes.SubtractOp):
            # return self.node_as_value(lhs) - self.node_as_value(rhs)
        # elif isinstance(node.op, nodes.DivisionOp):
            # return self.node_as_value(lhs) / self.node_as_value(rhs)
        # else:
            # raise RuntimeError()
        
    def visit_NaryOpExpr(self, node):
        newoperands = []
        for operand in node.operands:
            result = self.visit(operand)
            result = self.value_as_node(result)
            newoperands.append(result)
        node.operands = newoperands
        return node
        
    def visit_Function(self, node):
        # TODO: certain functions are handled specially:
        #   rgb(), hsl(), rgba(), hsla() become Colors
        node.expr = self.visit(node.expr)
        return node


#==============================================================================#

