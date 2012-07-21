from . import base
from .. import nodes

class Importer(base.NodeTransformer):
    def __init__(self, callback):
        self.callback = callback
        
    def visit_Import(self, node):
        if isinstance(node.uri, nodes.StringNode):
            # only import if uri is a string node
            newnode = self.callback(node.uri.string)
            if newnode:
                assert isinstance(newnode, nodes.Stylesheet)
                newnode = nodes.ImportedStylesheet(imports=newnode.imports, 
                                                   statements=newnode.statements)
                return newnode
        # do nothing
        return node
        
    def __call__(self, node):
        return self.visit(node)


