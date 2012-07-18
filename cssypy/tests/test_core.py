import re

from cssypy import core

from . import base

#==============================================================================#
COMMENT = r'(?:/\*(?:[^*]|\*[^/])*\*/)'
STRING = r'(?:{0})'.format('|'.join((r'"(?:\\[.]|[^"])*"', r"'(?:\\[.]|[^'])*'")))
WS = r'(?:[ \t\f\r\n]+)'

re_string = re.compile(STRING, re.UNICODE)
re_ws = re.compile(WS, re.UNICODE)

def normalize(s):
    r = u''
    p = 0
    while p < len(s):
        m = re_string.match(s, p)
        if m:
            r += m.group()
            p = m.end()
            continue
        m = re_ws.match(s, p)
        if m:
            r += u' '
            p = m.end()
            continue
        r += s[p]
        p += 1
    r = r.strip()
    return r


#==============================================================================#
class CompileString_TestCase(base.TestCaseBase):
    def test_empty(self):
        src = u''
        r = core.compile_string(src)
        self.assertEqual(u'', normalize(r))
        
    def test_not_unicode(self):
        src = ''
        with self.assertRaises(ValueError) as cm:
            core.compile_string(src)
    
    def test_simple(self):
        src = u'rule {}'
        r = core.compile_string(src)
        self.assertEqual(u'rule {}', normalize(r))
        
    def test_nested(self):
        src = u'outer { inner { rule: value; } }'
        expect = u'outer {} outer inner { rule: value; }'
        r = core.compile_string(src)
        self.assertEqual(expect, normalize(r))
    
    def test_values1(self):
        src = u'rule {a: "string"; b: #aabbcc; c: 1.5; d: 2em; e: 45% }'
        r = core.compile_string(src)
        self.assertEqual(u'rule { a: "string"; b: #aabbcc; c: 1.5; d: 2em; e: 45%; }', normalize(r))
    
    def test_solve_expr1(self):
        src = u'selector {a: 1+2+3+4; }'
        r = core.compile_string(src)
        self.assertEqual(u'selector { a: 10; }', normalize(r))
    
    def test_solve_expr2(self):
        src = u'selector {a: 1*2*3*4; }'
        r = core.compile_string(src)
        self.assertEqual(u'selector { a: 24; }', normalize(r))
    
    def test_solve_expr3(self):
        src = u'selector {a: 2*2+3*4; }'
        r = core.compile_string(src)
        self.assertEqual(u'selector { a: 16; }', normalize(r))
    
    def test_fwdslash(self):
        src = u'selector {a: 6/3; }'
        r = core.compile_string(src)
        self.assertEqual(u'selector { a: 6/3; }', normalize(r))
    
    def test_division1(self):
        src = u'selector {a: (6/3); }'
        r = core.compile_string(src)
        self.assertEqual(u'selector { a: 2; }', normalize(r))
    
    def test_division2(self):
        src = u'selector {a: 8/4+1; }'
        r = core.compile_string(src)
        self.assertEqual(u'selector { a: 3; }', normalize(r))
        
    def test_selectors(self):
        src = u'a#b .c, d:not(e) *[fgh], [i~=jk] :m ::n :before {}'
        exp = u'a#b .c, d:not(e) *[fgh], [i~=jk] :m ::n ::before {}'
        r = core.compile_string(src)
        self.assertEqual(exp, normalize(r))
    
    def test_function(self):
        src = u'selector {a: func("abc",15) ; }'
        r = core.compile_string(src)
        self.assertEqual(u'selector { a: func("abc", 15); }', normalize(r))
    
    def test_unaryop(self):
        src = u'selector {a: -5; }'
        r = core.compile_string(src)
        self.assertEqual(u'selector { a: -5; }', normalize(r))
        

#==============================================================================#
class CompileString_NoSolvers_TestCase(base.TestCaseBase):
    def test_paren1(self):
        src = u'selector { rule: 1*(2+3) } '
        expect = u'selector { rule: 1*(2+3); }'
        r = core.compile_string(src, do_solve=False)
        self.assertEqual(expect, normalize(r))
    
    def test_paren2(self):
        src = u'selector { rule: 1+(2-3) } '
        expect = u'selector { rule: 1+(2-3); }'
        r = core.compile_string(src, do_solve=False)
        self.assertEqual(expect, normalize(r))
    
    def test_unnecessary_paren1(self):
        src = u'selector { rule: (1+2)+3 } '
        expect = u'selector { rule: 1+2+3; }'
        r = core.compile_string(src, do_solve=False)
        self.assertEqual(expect, normalize(r))
    
    def test_unnecessary_paren2(self):
        src = u'selector { rule: (1*2)+3 } '
        expect = u'selector { rule: 1*2+3; }'
        r = core.compile_string(src, do_solve=False)
        self.assertEqual(expect, normalize(r))
    
    def test_unnecessary_paren3(self):
        src = u'selector { rule: (5) } '
        expect = u'selector { rule: 5; }'
        r = core.compile_string(src, do_solve=False)
        self.assertEqual(expect, normalize(r))
        

#==============================================================================#
class CompileString_NoImporters_TestCase(base.TestCaseBase):
    def test_empty(self):
        src = u''
        expect = u''
        r = core.compile_string(src, do_imports=False)
        self.assertEqual(expect, normalize(r))


#==============================================================================#