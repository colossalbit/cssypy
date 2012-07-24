from __future__ import absolute_import
from __future__ import print_function

class Stylesheet(object):
    def __init__(self, rootnode, filename='', encoding=None, forced_encoding=False, Parser=None):
        assert Parser
        self.rootnode = rootnode
        self.filename = filename
        self.encoding = encoding
        self.forced_encoding = forced_encoding
        self.Parser = Parser
        
    def update_rootnode(self, rootnode):
        assert self.rootnode
        self.rootnode = rootnode
        
    def has_charset(self):
        pass
        
    def get_charset(self):
        pass

