from .. import nodes, errors, csstokens as tokens
from ..utils import escapes
from . import base

def _create_string_node(value):
    return nodes.StringNode(escapes.unquote_string(value))

def _create_ident_node(value):
    return nodes.Ident(escapes.unescape_identifier(value))

def _create_ident_expr_node(value):
    return nodes.IdentExpr(escapes.unescape_identifier(value))


class Parser(base.ParserBase):
    
    def parse(self):
        return self.stylesheet()
    
    def stylesheet(self):
        """
        stylesheet ::= 
            charset?
            ( S | CDO | CDC )*
            ( import ( CDO S* | CDC S* )* )*
            ( toplevel_statement ( CDO S* | CDC S* )* )*
            ;
        """
        if not self.match(tokens.START):
            # TODO: should this have an error?
            pass
        # match @charset
        charset = self.charset()
        while self.match_any(tokens.WS, tokens.CDO, tokens.CDC):
            pass
        # TODO: match @import
        statements = []
        while self.peek().type != tokens.EOF:
            stmt = self.toplevel_statement()
            if not stmt:
                break
            statements.append(stmt)
            while self.match_any(tokens.CDO, tokens.CDC):
                self.skip_ws()
        if not self.match(tokens.EOF):
            # error, didn't parse entire file
            raise self.syntax_error("Expected end-of-file.")
        return nodes.Stylesheet(charset, statements)
        
    def charset(self):
        """
        charset ::= CHARSET_SYM STRING ';' ;
        """
        if self.match(tokens.CHARSET_SYM):
            if not self.match(tokens.STRING):
                self.syntax_error("Bad @charset rule.")
            charset = nodes.Charset(self.cur.value)
            if not self.match(tokens.SEMICOLON):
                self.syntax_error("Bad @charset rule.")
            return charset
        return None
        
    def toplevel_statement(self):
        """
        toplevel_statement ::= ruleset | media | page | vardef | mixin;
        # note: 'vardef' and 'mixin' are extensions to CSS
        """
        node = None
        tok = self.peek()
        if tok.type == tokens.VARNAME:
            # variable definition
            # TODO: Followed by ';' unless it's the end of the file (which 
            #       would make it a useless variable definition).
            node = self.vardef()
            if not self.match(tokens.SEMICOLON):
                peeker = self.peeker()
                peeker.skip_ws()
                if peeker.peek().type != tokens.EOF:
                    raise self.syntax_error("Variable definitions must end with a semicolon.")
        elif tok.type == tokens.MEDIA_SYM:
            # TODO: @media
            pass
        elif tok.type == tokens.PAGE_SYM:
            # TODO: @page
            pass
        elif tok.type == tokens.ATKEYWORD_OTHER:
            # TODO: @SOMETHING
            pass
        else:
            # TODO: In non-strict parsing mode:
            #       Ignore ruleset if we receieve a syntax error. Skip to end 
            #       of ruleset, which would be the closing RBRACE (accounting 
            #       for nested braces)
            node = self.ruleset()
        return node
        
    def inner_statement(self):
        """
        # standard CSS:
        inner_statement ::= declaration ;
        
        # extended:
        inner_statement ::= declaration | ruleset | vardef ;
        
        # note: 'vardef' is an extension to CSS
        """
        # A declaration and ruleset can both start with similar tokens.  Thus, 
        # we must read ahead to disambiguate.  Since this will most often be a 
        # declaration (we assume), we try that first.
        # 
        # (style) declaration
        # ruleset
        # atkeyword block
        #
        # IDENT S* ':' IDENT    -->  ruleset or declaration
        # IDENT S* ':' FUNCTION -->  ruleset or declaration
        # IDENT S* !':'         -->  ruleset only
        # IDENT S* ':' S+       -->  declaration only
        # VARNAME               -->  vardef only
        decl = self.declaration()
        if decl:
            return decl
        ruleset = self.ruleset()
        if ruleset:
            return ruleset
        vardef = self.vardef()
        if vardef:
            return vardef
        return None
        
    def ruleset(self):
        """
        ruleset ::= selector_group '{' S* ruleset_body '}' S* ;
        """
        selectors = self.selector_group()
        if not selectors:
            return None
        
        self.skip_ws()
        if not self.match(tokens.LBRACE):
            raise self.syntax_error("Expected left brace: '{'.")
        self.skip_ws()
        # quit now if body is empty
        if self.match(tokens.RBRACE):
            self.skip_ws()
            return nodes.RuleSet(selectors, [])
        
        self.skip_ws()
        statements = self.ruleset_body()
                
        if not self.match(tokens.RBRACE):
            raise self.syntax_error("Expected right brace: '}'.")
            
        self.skip_ws()
        
        return nodes.RuleSet(selectors, statements)
        
    def selector_group(self):
        """
        selector_group ::= selector ( ',' S* selector )* ;
        """
        selectors = []
        selector = self.selector()
        if not selector:
            return []
        selectors.append(selector)
        
        while self.match(tokens.COMMA):
            self.skip_ws() # skip optional whitespace
            selector = self.selector()
            if not selector:
                raise self.syntax_error("Expected selector.")
            selectors.append(selector)
            
        return selectors
        
    def ruleset_body(self):
        """
        ruleset_body ::= S* inner_statement? ( ';' S* inner_statement? )* ;
        
        ruleset_body ::= ( S* ( declaration | vardef )? ';' | S* ruleset ';'? )*
                         ( S* ( declaration | vardef | ruleset ) ';'? )? ;
                         
        # Semicolons required after declarations and vardefs unless they are 
        # the last item in the ruleset. Semicolons are never required after 
        # nested rulesets (but they are allowed).
        """
        # TODO: In non-strict parsing mode:
        #       If we find any errors while parsing a statement, discard that 
        #       statement and all following statements until we see an RBRACE 
        #       (accounting for nested braces).
        self.enter_nested_scope()
        
        try:
            statements = []
            stmt = self.inner_statement()
            if stmt:
                statements.append(stmt)
            
            while isinstance(stmt, nodes.RuleSet) or self.match(tokens.SEMICOLON):
                self.skip_ws()
                stmt = self.inner_statement()
                if stmt:
                    statements.append(stmt)
                
            return statements
        
        finally:
            self.exit_nested_scope()
        
        
    def selector(self):
        """
        selector ::= 
            simple_selector_sequence ( combinator simple_selector_sequence )*
            ;
        """
        # TODO: Note start/end of selector, so we can ensure there is no more 
        #       than one '&' in it.
        ssseq = self.simple_selector_sequence()
        if not ssseq:
            return None
        stor = nodes.Selector(ssseq)
        while True:     # pragma: no branch
            # Peek for common case of WS LBRACE which signals the start of the 
            # ruleset body.
            peeker = self.peeker()
            if peeker.match(tokens.WS):
                peeker.skip_ws()
                if peeker.match(tokens.LBRACE):
                    break
                # p += 1
                # while self.peek(p).type == tokens.WS:
                    # p += 1
                # if self.peek(p).type == tokens.LBRACE:
                    # # we've found the ruleset, so quit parsing this selector
                    # break
            
            comb = self.combinator()
            if not comb:
                break
            ssseq = self.simple_selector_sequence()
            if not ssseq:
                # TODO: Make sure this doesn't conflict with variable 
                #       definitions, which also fit 
                #       'simple_selector_sequence combinator' syntax: IDENT ':'
                # XXX: No, There is no conflict!!! 
                #      Variables are not IDENT tokens, they are VARNAME tokens.
                # Note: Without the above 'peek' for the start of a ruleset 
                #       body, this would raise on error if there was whitespace 
                #       between the last SimpleSelectorSequence and the opening 
                #       LBRACE of the ruleset body.  That's because the 
                #       whitespace would be matched as a combinator.
                raise self.syntax_error("Expected simple selector sequence.")
            stor.add_simple_selector_sequence(comb, ssseq)
        return stor
        
    def simple_selector_sequence(self):
        """
        simple_selector_sequence ::=
              simple_selector_sequence_head simple_selector_sequence_tail?
            | simple_selector_sequence_tail
            ;
        """
        head = self.simple_selector_sequence_head()
        tail = self.simple_selector_sequence_tail()
        tail = tail or []
        if not head and not tail:
            return None
        else:
            return nodes.SimpleSelectorSequence(head, tail)
        
    def type_selector(self):
        """
        type_selector ::= element_name ;
        """
        if self.match(tokens.IDENT):
            return nodes.TypeSelector(name=self.cur.value)
        return None
        
    def universal_selector(self):
        """
        universal_selector ::= '*' ;
        """
        if self.match(tokens.STAR):
            return nodes.UniversalSelector()
        return None
        
    def combine_ancestor_selector(self):
        """
        combine_ancestor_selector ::= '&' ;
        # note: extension to CSS
        """
        # non-standard CSS
        # TODO: only one CombineAncestorSelector allowed per selector
        if self.match(tokens.AMPERSAND):
            if not self.is_nested_scope():
                raise self.syntax_error("The '&' selector is only allowed within nested ruleset scopes.")
            return nodes.CombineAncestorSelector()
        return None
        
    _ssshead_dict = {
        tokens.IDENT: type_selector,
        tokens.STAR: universal_selector,
        tokens.AMPERSAND: combine_ancestor_selector,  # non-standard CSS
    }
    
    def simple_selector_sequence_head(self):
        """
        simple_selector_sequence_head 
            ::= ( type_selector | universal_selector | '&' ) ;
        # note: the '&' selector is an extension to CSS
        #       the '&' selector is only valid in nested CSS
        """
        rule = self._ssshead_dict.get(self.peek().type, None)
        if rule:
            node = rule(self)
            if not node:
                raise RuntimeError()  # TODO
            return node
        return None
        
    def id_selector(self):
        """
        idselector ::= HASH ;
        """
        if self.match(tokens.HASH):
            return nodes.IdSelector(self.cur.value)
        return None
    
    def class_selector(self):
        """
        class ::= '.' IDENT ;
        """
        if self.match(tokens.DOT):
            if self.match(tokens.IDENT):
                return nodes.ClassSelector(name=self.cur.value)
            else:
                raise self.syntax_error("Expected identifier.")
        return None
        
    _attrib_head_dict = {
        tokens.PREFIXMATCH:     nodes.AttrPrefixMatchOp,
        tokens.SUFFIXMATCH:     nodes.AttrSuffixMatchOp,
        tokens.SUBSTRINGMATCH:  nodes.AttrSubstringMatchOp,
        tokens.EQUAL:           nodes.AttrExactMatchOp,
        tokens.INCLUDES:        nodes.AttrIncludesMatchOp,
        tokens.DASHMATCH:       nodes.AttrDashMatchOp,
    }
        
    def attrib_selector(self):
        """
        attrib_selector ::= 
            '[' 
            S* IDENT S* 
            ( 
                ( 
                    PREFIXMATCH | SUFFIXMATCH | SUBSTRINGMATCH 
                    | '=' | INCLUDES | DASHMATCH 
                ) S* ( 
                    IDENT | STRING 
                ) S*
            )? 
            ']'
            ;
        """
        if self.match(tokens.LSQBRACKET):
            self.skip_ws()
            if not self.match(tokens.IDENT):
                self.syntax_error('Expected identifier')
            name = self.cur.value
            self.skip_ws()
            OpNode = self.match_dict(self._attrib_head_dict)
            if OpNode:
                op = OpNode()
                self.skip_ws()
                if self.match(tokens.IDENT):
                    val = nodes.IdentExpr(self.cur.value)
                elif self.match(tokens.STRING):
                    val = nodes.StringNode(self.cur.value)
                else:
                    self.syntax_error('Expected identifier or string.')
                self.skip_ws()
            else:
                op = None
                val = None
            if not self.match(tokens.RSQBRACKET):
                self.syntax_error("Expected right square bracket: ']'.")
            return nodes.AttributeSelector(name, op=op, val=val)
        return None
        
    def pseudo_selector(self):
        """
        pseudo_selector ::= ':' ':'? ( IDENT | function ) ;
        """
        if self.match(tokens.COLON):
            pseudo_elem = False
            if self.match(tokens.COLON):
                pseudo_elem = True
            if self.match(tokens.IDENT):
                if self.cur.value.lower() in ('first-line','first-letter','before','after'):
                    pseudo_elem = True
                child = nodes.Ident(self.cur.value)
            elif seek.peek().type == tokens.FUNCTION:
                child = self.function()
            else:
                # TODO: error or not?
                self.syntax_error('Expected identifier or function in pseudo-selector.')
            
            if pseudo_elem:
                return nodes.PseudoElementSelector(child)
            else:
                return nodes.PseudoClassSelector(child)
                
                
            # if self.match(tokens.IDENT):
                # ident = nodes.Ident(self.cur.value)
                # return nodes.PseudoSelector(ident)
            
            # elif self.peek().type == tokens.FUNCTION:
                # func = self.function()
                # return nodes.PseudoSelector(func)
        
        return None
        
    _negarg_rules = (
        type_selector, 
        universal_selector, 
        id_selector, 
        class_selector, 
        attrib_selector, 
        pseudo_selector,
    )
        
    def negation_selector(self):
        """
        negation_selector ::= NOT S* negation_arg S* ')' ;
        """
        if self.match(tokens.NOT):
            self.skip_ws()
            for rule in self._negarg_rules:
                arg = rule(self)
                if arg:
                    node = nodes.NegationSelector(arg)
                    break
            else:
                # no rules matched
                self.syntax_error('Unrecognized not() argument.')
            self.skip_ws()
            if not self.match(tokens.RPAREN):
                self.syntax_error('Expected right parenthesis.')
            return node
        return None
        
    _ssstail_dict = {
        tokens.HASH: id_selector,
        tokens.DOT: class_selector,
        tokens.LSQBRACKET: attrib_selector,
        tokens.COLON: pseudo_selector,
        tokens.NOT: negation_selector,
    }
        
    def simple_selector_sequence_tail(self):
        """
        simple_selector_sequence_tail ::=
            ( HASH | class_selector | attrib_selector | pseudo_selector | negation_selector )+
            ;
        """
        nodelist = []
        while True:
            rule = self._ssstail_dict.get(self.peek().type, None)
            if not rule:
                break
            node = rule(self)
            if not node:
                raise RuntimeError()  # TODO
            nodelist.append(node)
        return nodelist
        
    def combinator(self):
        """
        combinator ::= PLUS S* | GREATERTHAN S* | TILDE S* | S+ ;
        """
        #  S* '+' S*  -> AdjacentSiblingCombinator
        #  S* '>' S*  -> ChildCombinator
        #  S* '~' S*  -> GeneralSiblingCombinator
        #  S+ !( '+' | '>' | '~' | '{' | ',' | ';' )  >peek>  IDENT | CLASS | HASH | UNIVERSAL | VARNAME | AMPERSAND | COLON |   ->  DescendantCombinator
        ws = False
        if self.match(tokens.WS):
            ws = True
            self.skip_ws()
        if self.match(tokens.PLUS):
            self.skip_ws()
            return nodes.AdjacentSiblingCombinator()
            
        elif self.match(tokens.GREATERTHAN):
            self.skip_ws()
            return nodes.ChildCombinator()
            
        elif self.match(tokens.TILDE):
            self.skip_ws()
            return nodes.GeneralSiblingCombinator()
            
        elif ws:
            return nodes.DescendantCombinator()
        return None
        
    def vardef(self):
        """
        vardef ::= VARNAME S* ':' S* expr ;
        """
        if self.match(tokens.VARNAME):
            name = self.cur.value
            self.skip_ws()
            if not self.match(tokens.COLON):
                raise self.syntax_error("Expected ':'.")
            self.skip_ws()
            expr = self.math_expr()
            if not expr:
                raise self.syntax_error("Expected expression.")
            return nodes.VarDef(name, expr)
        return None
    
    def declaration(self):
        """
        declaration ::= property ':' S* comma_expr prio? ;
        """
        # NOTE: selector and declaration can both begin IDENT, or IDENT COLON, or IDENT COLON IDENT
        # TODO: if tokens are ... SEMICOLON, ... COLON WS, we have declaration
        # TODO: if tokens are ... LBRACE, ... DOT, ... GREATERTHAN, ... TILDE, not IDENT, we have an inner_statement
        with self.token_stack_context() as token_stack:
            must_be_declaration = False
            
            prop = self.property()
            if not prop:
                return None
            
            if not self.match(tokens.COLON):
                return None
            
            # if we find WS here (after colon), this cannot be a selector, so it must be a declaration
            if self.skip_ws():
                token_stack.accept()
                must_be_declaration = True
            
            expr = self.comma_expr()
            if not expr:
                if must_be_declaration:
                    raise self.syntax_error("Expected expression.")
                else:
                    return None
            
            important = False
            if self.match(tokens.IMPORTANT_SYM):  # optional
                important = True
                token_stack.accept()
                must_be_declaration = True
            self.skip_ws()
            
            # next token should be SEMICOLON or RBRACE
            if self.peek().type not in (tokens.SEMICOLON, tokens.RBRACE):
                if must_be_declaration:
                    raise self.syntax_error("Expected ';' or '}'.")
                else:
                    return None
            
            return nodes.Declaration(prop=prop, expr=expr, important=important)
        
    def property(self):
        """
        property ::= IDENT S* ;
        """
        if self.match(tokens.IDENT):
            prop = nodes.Property(name=self.cur.value)
            self.skip_ws()
            return prop
        return None
    
    def paren_expr(self):
        """
        paren_expr ::= '(' S* math_expr ')' ;
        """
        if self.match(tokens.LPAREN):
            self.enter_paren_expr()
            try:
                self.skip_ws()
                expr = self.math_expr()
                self.skip_ws()
            finally:
                self.exit_paren_expr()
            if not self.match(tokens.RPAREN):
                raise self.syntax_error("Expected closing parenthesis.")
            return expr
        else:
            return None
            
    def _check_fwdslash_op(self, op, lhs, rhs):
        assert isinstance(op, nodes.FwdSlashOp)
        if isinstance(lhs, nodes.BinaryOpExpr) or isinstance(rhs, nodes.BinaryOpExpr):
            return nodes.DivisionOp()
        
        cur = lhs
        while isinstance(cur, nodes.UnaryOpExpr):
            cur = cur.operand
        if isinstance(cur, nodes.BinaryOpExpr) or isinstance(cur, nodes.VarName):
            return nodes.DivisionOp()
        
        cur = rhs
        while isinstance(cur, nodes.UnaryOpExpr):
            cur = cur.operand
        if isinstance(cur, nodes.BinaryOpExpr) or isinstance(cur, nodes.VarName):
            return nodes.DivisionOp()
        
        return op
    
    def comma_expr(self):
        """
        comma_expr ::= term ( comma_expr_operator? term )* S* ;
        
        # COMMA and WS operators are allowed in comma expressions.
        """
        term = self.term()
        if not term:
            return None
        node_stack = [term]
        op_stack = []
        
        while True:
            operator = self.comma_expr_operator()
            term = self.term()
            if operator and not term:
                if isinstance(operator, nodes.WhitespaceOp):
                    break
                raise self.syntax_error("Expected term.")
            elif not operator and not term:
                break
            elif not operator:
                print 'node_stack: {0}'.format(node_stack)
                print 'op_stack:   {0}'.format(op_stack)
                print 'term:       {0}'.format(term)
                raise self.syntax_error("Expected operator.")
            
            while op_stack and operator._precedence <= op_stack[-1]._precedence:
                op = op_stack.pop()
                rhs, lhs = node_stack.pop(), node_stack.pop()
                if op._nary:
                    if isinstance(lhs, nodes.NaryOpExpr) and lhs.op == op:
                        lhs.operands.append(rhs)
                    else:
                        lhs = nodes.NaryOpExpr(op, lhs, rhs)
                else:
                    # if lhs or rhsis BinaryOpExpr with FwdSlashOp, convert to DivisionOp
                    if isinstance(lhs, nodes.BinaryOpExpr) and isinstance(lhs.op, nodes.FwdSlashOp):
                        lhs.op = nodes.DivisionOp()
                    if isinstance(rhs, nodes.BinaryOpExpr) and isinstance(rhs.op, nodes.FwdSlashOp):
                        rhs.op = nodes.DivisionOp()
                    if isinstance(op, nodes.FwdSlashOp):
                        op = self._check_fwdslash_op(op, lhs, rhs)
                    lhs = nodes.BinaryOpExpr(op, lhs, rhs)
                node_stack.append(lhs)
                
            node_stack.append(term)
            op_stack.append(operator)
        
        while op_stack:
            op = op_stack.pop()
            rhs, lhs = node_stack.pop(), node_stack.pop()
            if op._nary:
                if isinstance(lhs, nodes.NaryOpExpr) and lhs.op == op:
                    lhs.operands.append(rhs)
                else:
                    lhs = nodes.NaryOpExpr(op, lhs, rhs)
            else:
                # if lhs or rhsis BinaryOpExpr with FwdSlashOp, convert to DivisionOp
                if isinstance(lhs, nodes.BinaryOpExpr) and isinstance(lhs.op, nodes.FwdSlashOp):
                    lhs.op = nodes.DivisionOp()
                if isinstance(rhs, nodes.BinaryOpExpr) and isinstance(rhs.op, nodes.FwdSlashOp):
                    rhs.op = nodes.DivisionOp()
                if isinstance(op, nodes.FwdSlashOp):
                    op = self._check_fwdslash_op(op, lhs, rhs)
                lhs = nodes.BinaryOpExpr(op, lhs, rhs)
            node_stack.append(lhs)
            
        self.skip_ws()
        assert len(node_stack) == 1
        return node_stack[0]
            
    def math_expr(self):
        """
        math_expr ::= term ( math_expr_operator? term )* S* ;
        
        # COMMA and WS operators are not allowed in math expressions.
        """
        term = self.term()
        if not term:
            return None
        node_stack = [term]
        op_stack = []
        
        while True:
            operator = self.math_expr_operator()
            term = self.term()
            if operator and not term:
                raise self.syntax_error("Expected term.")
            elif not operator and not term:
                break
            elif not operator:
                print 'node_stack: {0}'.format(node_stack)
                print 'op_stack:   {0}'.format(op_stack)
                print 'term:       {0}'.format(term)
                raise self.syntax_error("Expected operator.")
            
            while op_stack and operator._precedence <= op_stack[-1]._precedence:
                op = op_stack.pop()
                rhs, lhs = node_stack.pop(), node_stack.pop()
                assert not op._nary
                lhs = nodes.BinaryOpExpr(op, lhs, rhs)
                node_stack.append(lhs)
                
            node_stack.append(term)
            op_stack.append(operator)
        
        while op_stack:
            op = op_stack.pop()
            rhs, lhs = node_stack.pop(), node_stack.pop()
            assert not op._nary
            lhs = nodes.BinaryOpExpr(op, lhs, rhs)
            node_stack.append(lhs)
            
        self.skip_ws()
        assert len(node_stack) == 1
        return node_stack[0]

    def comma_expr_operator(self):
        """
        comma_expr_operator ::= 
              S* '/' S*
            | S* ',' S*
            | '*'
            | '+'
            | '-'  # not possible if preceded by IDENT, VARNAME, DIMENSION, or 
                   # HASH because '-' is allowed in those tokens
            | S+
        """
        ws = self.skip_ws()
        if self.match(tokens.FWDSLASH):
            self.skip_ws()
            return nodes.FwdSlashOp()  # Might be separator or division. Depends on expression contents.
        elif self.match(tokens.COMMA):
            self.skip_ws()
            return nodes.CommaOp()
        elif ws:
            return nodes.WhitespaceOp()
        else:
            # no WS
            if self.match(tokens.PLUS):
                if self.peek().type != tokens.WS:
                    return nodes.AddOp()
                else:
                    self.putback(self.cur)
            elif self.match(tokens.MINUS):
                if self.peek().type != tokens.WS:
                    return nodes.SubtractOp()
                else:
                    self.putback(self.cur)
            elif self.match(tokens.STAR):
                if self.peek().type != tokens.WS:
                    return nodes.MultOp()
                else:
                    self.putback(self.cur)
        return None
        
    def math_expr_operator(self):
        """
        math_expr_operator ::= 
              S* '/' S*
            | S* '*' S*
            | S* '+' S*
            | S* '-' S*
        """
        peeker = self.peeker()
        peeker.skip_ws()
        if peeker.match(tokens.FWDSLASH):
            peeker.commit()
            self.skip_ws()
            return nodes.DivisionOp()  # division (not a separator)
        elif peeker.match(tokens.STAR):
            peeker.commit()
            self.skip_ws()
            return nodes.MultOp()
        elif peeker.match(tokens.PLUS):
            peeker.commit()
            self.skip_ws()
            return nodes.AddOp()
        elif peeker.match(tokens.MINUS):
            peeker.commit()
            self.skip_ws()
            return nodes.SubtractOp()
        return None

    _term_dict = {
        tokens.NUMBER:          nodes.NumberNode,
        tokens.PERCENTAGE:      nodes.PercentageNode,
        tokens.DIMENSION:       nodes.DimensionNode,
        tokens.STRING:          nodes.StringNode,
        tokens.BADSTRING:       nodes.StringNode,
        tokens.IDENT:           nodes.IdentExpr,
        tokens.URI:             nodes.UriNode,
        tokens.BADURI:          nodes.UriNode,
        tokens.VARNAME:         nodes.VarName,
    }
        
    def term(self):
        """
        term ::= 
            unary_operator? ( 
                  NUMBER    | PERCENTAGE | LENGTH 
                | EMS       | EXS        | ANGLE    | TIME      | FREQ 
                | STRING    | IDENT      | URI      | VARNAME
                | hexcolor  | function   | '(' expr ')'
            ) 
            S* 
            ;
        
        term ::= ( '-' | '+' )? ( VALUE | IDENT | VARNAME | function | paren_expr ) ;
        
        # note: the parenthesized expression is an extension to CSS
        # note: VARNAME is an extension to CSS
        # note: Standard CSS allows a unary_operator before some of these rules 
        #       only.  We accept them before all rules to simplify the code.
        """
        with self.token_stack_context() as token_stack:
            term = None
            unary_op = self.unary_operator()  # optional
            func = self.match_dict(self._term_dict)
            if func:
                term = func(self.cur.value)
            elif self.peek().type == tokens.FUNCTION:
                term = self.function()
                if not term:
                    # syntax error, should have been handled in self.function()
                    pass
            elif self.peek().type == tokens.HASH:
                term = self.hexcolor()
                if not term:
                    # syntax error, should have been handled in self.hexcolor()
                    pass
            elif self.peek().type == tokens.LPAREN:
                term = self.paren_expr()
                if not term:
                    # syntax error, should have been handled in self.paren_expr()
                    pass
            if term:
                if unary_op:
                    term = nodes.UnaryOpExpr(op=unary_op, operand=term)
                token_stack.accept()
                ##self.skip_ws()
            return term
            
    def unary_operator(self):
        """
        unary_operator ::= '-' | '+' ;
        """
        if self.match(tokens.MINUS):
            return nodes.UMinus()
        elif self.match(tokens.PLUS):
            return nodes.UPlus()
        return None
        
    def function(self):
        """
        function ::= FUNCTION S* comma_expr ')' S* ;
        """
        if self.match(tokens.FUNCTION):
            name = self.cur.value
            self.skip_ws()
            expr = self.comma_expr()
            if not self.match(tokens.RPAREN):
                raise self.syntax_error("Expected ')' after function.")
            self.skip_ws()
            return nodes.FunctionExpr(name, expr)
        return None
            
    def hexcolor(self):
        """
        hexcolor ::= HASH S* ;
        """
        if self.match(tokens.HASH):
            hexcolor = nodes.HexColorNode(self.cur.value)
            self.skip_ws()
            return hexcolor
        return None







