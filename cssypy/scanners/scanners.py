from __future__ import absolute_import
from __future__ import print_function

import re
import itertools

from ..utils.py3compat import range
from .. import csstokens as tokens

class ScannerBase(object):
    def __init__(self, data):
        self._tokeniter = tokens.re_tokens.finditer(data)
        self._lineno = 1
        self._column = 1
        self._eof_count = 0
        self._next = [tokens.Token(tokens.START, u'', self._lineno, self._column)]
        
    def __iter__(self):
        return self
        
    def next(self):
        tok = self._next.pop(0)
        if not self._next:
            self._fill(10)
        return tok
        
    def _fill(self, n=1, force=False):
        # n: The desired length for self._next.
        ntoload = max(n - len(self._next), 0)
        i = -1
        try:
            for i in range(ntoload):
                self._next.append(self.get_next())
            return len(self._next)
        except StopIteration:
            if not force and self._eof_count > 1:
                raise
        loaded = i+1
        k = -1
        for k in range(ntoload - loaded):
            self._eof_count += 1
            self._next.append(tokens.Token(tokens.EOF, u'', self._lineno, self._column))
        return len(self._next)
        
    def putback(self, *toks):
        self._next[:0] = list(toks)
        
    def peek(self, n=0):
        try:
            return self._next[n]
        except IndexError:
            pass
        try:
            sz = max(n+1, 10)
            end = self._fill(n=sz, force=True)
            assert end > 0
            return self._next[min(end-1, n)]
        except StopIteration:
            return self._next[-1]  # this will be EOF
        
    def process_newlines(self, s):
        lines = tokens.re_newline.split(s)
        # returns: number_of_newlines, length_of_last_line
        return len(lines) - 1, len(lines[-1])
        
    embedded_newlines = set((tokens.STRING, tokens.COMMENT, tokens.WS, 
                             tokens.URI, tokens.BADCOMMENT, tokens.BADSTRING, 
                             tokens.BADURI, tokens.IDENT, 
                             tokens.ATKEYWORD_OTHER, tokens.DIMENSION,
                             tokens.HASH, tokens.FUNCTION))
    
    def advance_position(self, toktype, value):
        if toktype in self.embedded_newlines:
            nlines, nlast = self.process_newlines(value)
            if nlines:
                self._lineno += nlines
                self._column = nlast + 1
            else:
                self._column += len(value)
        else:
            self._column += len(value)
        
    def get_next(self):
        m = self._tokeniter.next()
        toktype = tokens.tokens[m.lastgroup]
        value = m.group()
        tok = tokens.Token(toktype, value, self._lineno, self._column)
        self.advance_position(toktype, value)
        ##print 'Token: {0}'.format(tok.typestr)
        return tok


class Scanner(ScannerBase):
    ignore_tokens = (tokens.COMMENT,)
    
    def get_next(self):
        tok = super(Scanner, self).get_next()
        while tok.type in self.ignore_tokens:
            tok = super(Scanner, self).get_next()
        return tok
        
        
#==============================================================================#
def benchmark_iter(src, tests=5):       # pragma: no cover
    import time
    times = []
    for i in range(tests):
        start = time.clock()
        for tok in re_tokens.finditer(src):
            pass
        stop = time.clock()
        times.append(stop - start)
    return times

def benchmark_iterlist(src, tests=5):   # pragma: no cover
    import time
    times = []
    for i in range(tests):
        start = time.clock()
        ilist = list(re_tokens.finditer(src))
        for tok in ilist:
            pass
        stop = time.clock()
        times.append(stop - start)
    return times
    
def benchmark_list(src, tests=5):       # pragma: no cover
    import time
    times = []
    for i in range(tests):
        start = time.clock()
        for tok in re_tokens.findall(src):
            pass
        stop = time.clock()
        times.append(stop - start)
    return times

def benchmark(src, ntests=5):           # pragma: no cover
    times_list = benchmark_list(src, tests=ntests)
    times_iterlist = benchmark_iterlist(src, tests=ntests)
    times_iter = benchmark_iter(src, tests=ntests)
    print('iter     time: {0}'.format(min(times_iter)))
    print('iterlist time: {0}'.format(min(times_iterlist)))
    print('list     time: {0}'.format(min(times_list)))

#==============================================================================#


