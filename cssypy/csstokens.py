import re

#==============================================================================#
# Token definition helpers

token_lookup = {}   # id -> name
tokens = {}         # name -> id
token_regexes = []  # regexes as strings (compiled at the end of this module)

# token families
BAD_TOKEN =        0x80000000
DELIM_TOKEN =      0x00010000
DIMENSION_TOKEN =  0x00020000
ATKEYWORD_TOKEN =  0x00040000
EXTENSION_TOKEN =  0x10000000  # not standard CSS

nextid = 0x1

def tok(name, regex=None, id=None, ext=False, family=0):
    global nextid
    id = id or nextid
    id |= family
    if ext:
        id |= EXTENSION_TOKEN
    globals()[name] = id
    tokens[name] = id
    token_lookup[id] = name
    if regex is not None:
        token_regexes.append(r'(?P<{0}>{1})'.format(name, regex))
    nextid += 1
    
def bad(name, regex=None, ext=False):
    tok(name, regex, ext=ext, family=BAD_TOKEN)
    
def delim(name, regex=None, ext=False):
    tok(name, regex, ext=ext, family=DELIM_TOKEN)
    
def dim(name, regex=None, ext=False):
    tok(name, regex, ext=ext, family=DIMENSION_TOKEN)
    
def at(name, regex=None, ext=False):
    tok(name, regex, ext=ext, family=ATKEYWORD_TOKEN)

#==============================================================================#
# Token Class

class Token(object):
    __slots__ = ('type', 'value', 'lineno', 'column')
    
    def __init__(self, type, value, lineno, column):
        self.type = type
        self.value = value
        self.lineno = lineno
        self.column = column
        
    @property
    def typestr(self):
        return token_lookup[self.type]
        
        
#==============================================================================#
# Token regexes

# common components
nonascii = r'(?:[^\0-\237])'
unicode = r'(?:\\[0-9a-fA-F]{1,6}(?:\r\n|[ \n\r\t\f])?)'
nl = r'(?:\n|\r\n|\r|\f)'
w = r'(?:[ \t\r\n\f]*)'
escape = r'(?:{unicode}|\\[^\n\r\f0-9a-fA-F])'.format(unicode=unicode)
nmstart = r'(?:[_a-zA-Z]|{nonascii}|{escape})'.format(nonascii=nonascii, escape=escape)
nmchar = r'(?:[_a-zA-Z0-9-]|{nonascii}|{escape})'.format(nonascii=nonascii, escape=escape)
name = r'(?:{nmchar}+)'.format(nmchar=nmchar)
num = r'(?:[0-9]*\.[0-9]+|[0-9]+)'

# strings
string1 = r'(?:"(?:[^\n\r\f\\"]|\\{nl}|{escape})*")'.format(nl=nl, escape=escape)
string2 = r"(?:'(?:[^\n\r\f\\']|\\{nl}|{escape})*')".format(nl=nl, escape=escape)
string = r'(?:{string1}|{string2})'.format(string1=string1, string2=string2)

badstring1 = r'(?:"(?:[^\n\r\f\\"]|\\{nl}|{escape})*\\?)'.format(nl=nl, escape=escape)
badstring2 = r"(?:'(?:[^\n\r\f\\']|\\{nl}|{escape})*\\?)".format(nl=nl, escape=escape)
badstring = r'(?:{badstring1}|{badstring2})'.format(badstring1=badstring1, badstring2=badstring2)

# comments
comment = r'(?:/\*[^*]*\*+(?:[^/*][^*]*\*+)*/)'
badcomment1 = r'(?:/\*[^*]*\*+(?:[^/*][^*]*\*+)*)'
badcomment2 = r'(?:/\*[^*]*(\*+?:[^/*][^*]*)*)'
badcomment = r'(?:{badcomment1}|{badcomment2})'.format(badcomment1=badcomment1, badcomment2=badcomment2)

# uri
url = r'(?:(?:[!#$%&*-\[\]-~]|{nonascii}|{escape})*)'.format(nonascii=nonascii, escape=escape)
uri1 = r'(?:url\({w}{string}{w}\))'.format(w=w, string=string)
uri2 = r'(?:url\({w}{url}{w}\))'.format(w=w, url=url)
uri = r'(?:{uri1}|{uri2})'.format(uri1=uri1, uri2=uri2)
baduri1 = r'(?:url\({w}{url}{w})'.format(w=w, url=url)
baduri2 = r'(?:url\({w}{string}{w})'.format(w=w, string=string)
baduri3 = r'(?:url\({w}{badstring})'.format(w=w, badstring=badstring)
baduri = r'(?:{baduri1}|{baduri2}|{baduri3})'.format(baduri1=baduri1, baduri2=baduri2, baduri3=baduri3)

# identifiers (and similar)
ident = r'(?:-?{nmstart}{nmchar}*)'.format(nmstart=nmstart, nmchar=nmchar)
import_sym = r'(?:@[Ii][Mm][Pp][Oo][Rr][Tt]\b)'
page_sym = r'(?:@[Pp][Aa][Gg][Ee]\b)'
media_sym = r'(?:@[Mm][Ee][Dd][Ii][Aa]\b)'
charset_sym = r'(?:@charset )'  # trailing space is deliberate
important_sym = r'(?:!{w}[Ii][Mm][Pp][Oo][Rr][Tt][Aa][Nn][Tt]\b)'.format(w=w)
atkeyword = r'(?:@{ident})'.format(ident=ident)
varname = r'(?:\${ident})'.format(ident=ident)
function = r'(?:{ident}\()'.format(ident=ident)
hash = r'(?:#{name})'.format(name=name)

# numbers (and similar)
percentage = r'(?:{num}%)'.format(num=num)
dimension = r'(?:{num}{ident})'.format(num=num, ident=ident)
number = r'(?:{num})'.format(num=num)

unicode_range = r'(?:u\+[0-9A-Fa-f?]{1,6}(?:-[0-9A-Fa-f]{1,6})?)'
ws = r'(?:[ \t\r\n\f]+)'

# django-specific
django_template_tag = r'(?:\{%(?:[^\n\r%\'"]|%[^\n\r\}\'"]|"[^\n\r"]*"|\'[^\n\r\']*\')*%\})'
django_template_variable = r'(?:\{\{(?:[^\n\r\{\}\'"]|"[^\n\r"]*"|\'[^\n\r\']*\')*\}\})'


#==============================================================================#
# Token definitions -- Order is important!

tok('START')    # no corresponding regex
tok('EOF')      # no corresponding regex

tok('WS',   ws)

tok('URI',              uri)            # must precede UNICODE_RANGE, FUNCTION, and IDENT
bad('BADURI',           baduri)
tok('UNICODE_RANGE',    unicode_range)  # must precede IDENT
tok('FUNCTION',         function)       # must precede IDENT
tok('IDENT',            ident)
tok('VARNAME',          varname, ext=True)

tok('HASH',             hash)
dim('DIMENSION',        dimension)      # must precede NUMBER
tok('PERCENTAGE',       percentage)     # must precede NUMBER
tok('NUMBER',           number)

# longer operators must precede shorter operators
tok('CDO',              r'<!--')
tok('CDC',              r'-->')
tok('NOT',              r':[Nn][Oo][Tt]\(')                 # must precede COLON
tok('DJANGO_TTAG',      django_template_tag, ext=True)      # must precede LBRACE
tok('DJANGO_TVAR',      django_template_variable, ext=True) # must precede LBRACE
tok('COLON',            r':')
tok('SEMICOLON',        r';')

tok('LBRACE',           r'\{')
tok('RBRACE',           r'\}')
tok('LPAREN',           r'\(')
tok('RPAREN',           r'\)')
tok('LSQBRACKET',       r'\[')
tok('RSQBRACKET',       r'\]')

tok('STRING',           string)
bad('BADSTRING',        badstring)

tok('COMMENT',          comment)        # must precede FWDSLASH
bad('BADCOMMENT',       badcomment)

tok('IMPORTANT_SYM',    important_sym)  # must precede EXCLAMATION
at('IMPORT_SYM',        import_sym)
at('PAGE_SYM',          page_sym)
at('MEDIA_SYM',         media_sym)
at('CHARSET_SYM',       charset_sym)
at('ATKEYWORD_OTHER',   atkeyword)      # must come after other at-keywords

tok('INCLUDES',         r'~=')          # must precede TILDE
tok('DASHMATCH',        r'\|=')         # must precede PIPE
tok('PREFIXMATCH',      r'\^=')         # must precede CARET
tok('SUFFIXMATCH',      r'\$=')
tok('SUBSTRINGMATCH',   r'\*=')         # must precede STAR

delim('COMMA',          r',')
delim('DOT',            r'\.')
delim('PLUS',           r'\+')
delim('CARET',          r'\^')
delim('AMPERSAND',      r'&', ext=True)
delim('LESSTHAN',       r'<')
delim('GREATERTHAN',    r'>')
delim('STAR',           r'\*')
delim('FWDSLASH',       r'/')
delim('PIPE',           r'\|')
delim('EXCLAMATION',    r'!')
delim('TILDE',          r'~')
delim('MINUS',          r'-')
delim('EQUAL',          r'=')

tok('UNKNOWN',          r'.')           # UNKNOWN must be last


#==============================================================================#
# regex definitions -- used by the scanner

token_str = '|'.join(token_regexes)

re_tokens = re.compile(token_str)
re_newline = re.compile(nl)

