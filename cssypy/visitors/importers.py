from . import base
from .. import nodes

class Importer(base.NodeTransformer):
    def __init__(self, callback):
        self.callback = callback
        
    def visit_Import(self, node):
        # TODO: 
        #   Get url from node.
        #   Call callback with url.
        #   If callback doesn't return None, replace node with return value.
        return node
        
    def __call__(self, node):
        return self.visit(node)


