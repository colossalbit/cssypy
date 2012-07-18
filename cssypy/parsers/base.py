from .. import errors, csstokens as tokens
from ..scanners import Scanner

from .util import TokenStackContext, Peeker


class ParserBase(object):
    def __init__(self, data, filename=''):
        self.scanner = Scanner(data)
        self._cur = None
        self._token_stacks = []
        self._nested_level = 0
        self._paren_level = 0
        self._filename = filename or '<FILENAME>'
        
    @property
    def cur(self):
        """Is only safe to access immediately after a call 'match' or 
           'match_any' that returned True.  Otherwise, an intervening call to 
           'putback' will mean this is inaccurate.
        """
        return self._cur

    def peek(self, n=0):
        tok = self.scanner.peek(n)
        # if tok.type == UNKNOWN, BADCOMMENT, BADURI, or BADSTRING, raise exception
        return tok
        
    def peeker(self, pos=0):
        return Peeker(self, pos)
        
    def putback(self, *toks):
        self.scanner.putback(*toks)
        
    def advance(self, n):
        for i in xrange(n):
            self._cur = self.scanner.next()
            if self._token_stacks:
                self._token_stacks[-1].append(self._cur)
        
    def match(self, toktype):
        tok = self.peek()
        if tok.type == toktype:
            self._cur = self.scanner.next()
            if self._token_stacks:
                self._token_stacks[-1].append(self._cur)
            return True
        return False
        
    def match_any(self, *toktypes):
        tok = self.peek()
        if tok.type in toktypes:
            self._cur = self.scanner.next()
            if self._token_stacks:
                self._token_stacks[-1].append(self._cur)
            return True
        return False
        
    def match_dict(self, dct):
        tok = self.peek()
        func = dct.get(tok.type, None)
        if func is not None:
            self._cur = self.scanner.next()
            if self._token_stacks:
                self._token_stacks[-1].append(self._cur)
        return func
        
    def skip_ws(self):
        count = 0
        while self.match(tokens.WS):
            count += 1
        return count
        
    def token_stack_push(self):
        self._token_stacks.append([])
        
    def token_stack_pop(self):
        # TODO: merge top token stack into next token stack?
        toks = self._token_stacks.pop()
        if self._token_stacks:
            self._token_stacks[-1].extend(toks)
        
    def token_stack_putback(self):
        self.putback(*self._token_stacks[-1])
        self._token_stacks[-1] = []
        
    def token_stack_context(self):
        return TokenStackContext(self)
        
    def syntax_error(self, msg, use_next_token=True):
        if use_next_token:
            tok = self.peek()
        else:
            tok = self.cur
        # return here so we can raise at call site
        return errors.CSSSyntaxError(msg, filename=self._filename, 
                                     lineno=tok.lineno, column=tok.column, 
                                     token=tok)
        
    def is_nested_scope(self):
        return self._nested_level > 0
        
    def enter_nested_scope(self):
        self._nested_level += 1
        
    def exit_nested_scope(self):
        self._nested_level -= 1
        
    def is_paren_expr(self):
        return self._paren_level > 0
        
    def enter_paren_expr(self):
        self._paren_level += 1
        
    def exit_paren_expr(self):
        self._paren_level -= 1


