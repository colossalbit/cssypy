from .. import csstokens as tokens

class TokenStackContext(object):
    def __init__(self, parser):
        self.parser = parser
        self._accept = False
    
    def __enter__(self):
        self.parser.token_stack_push()
        return self
    
    def __exit__(self, exc_type, exc_value, tb):
        if not self._accept:
            self.parser.token_stack_putback()
        self.parser.token_stack_pop()
        
    def accept(self, b=True):
        self._accept = b
        
        
class Peeker(object):
    def __init__(self, parser, pos=0):
        self._scanner = parser.scanner
        self._parser = parser
        self._pos = pos
        
    def reset(self):
        self._pos = 0
        
    def match(self, type):
        if self._scanner.peek(self._pos).type == type:
            self._pos += 1
            return True
        return False
        
    def peek(self, n=0):
        return self._scanner.peek(self._pos + n)
            
    def skip_ws(self):
        start = self._pos
        while self._scanner.peek(self._pos).type == tokens.WS:
            self._pos += 1
        return self._pos - start
        
    def commit(self):
        self._parser.advance(self._pos)
        self.reset()
