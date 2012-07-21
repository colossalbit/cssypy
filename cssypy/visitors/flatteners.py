from .base import NodeTransformer
from .. import nodes

#==============================================================================#
class RulesetChain(object):
    def __init__(self, selectors, statements):
        assert isinstance(selectors, list)
        assert all(isinstance(sel, nodes.Selector) for sel in selectors)
        assert isinstance(statements, list)
        self.selector_seqs = [[s] for s in selectors]
        self.statements = statements
        
    def prepend_selectors(self, selectors):
        assert isinstance(selectors, list)
        if not selectors:
            return
        elif len(selectors) == 1:
            for selector_seq in self.selector_seqs:
                selector_seq.insert(0, selectors[0])
        else:
            new_selector_seqs = []
            for selector_seq in self.selector_seqs:
                for selector in selectors:
                    new_selector_seq = [selector] + selector_seq
                    new_selector_seqs.append(new_selector_seq)
            self.selector_seqs = new_selector_seqs
            
    def _resolve_selector(self, ancestors, selector):
        assert isinstance(ancestors, list)
        assert isinstance(selector, nodes.Selector)
        if not ancestors:
            return selector.children[:]
        for i,node in enumerate(selector.children):
            if isinstance(node, nodes.SimpleSelectorSequence) and isinstance(node.head, nodes.CombineAncestorSelector):
                newseq = selector.children[:]
                if node.tail:
                    assert isinstance(ancestors[-1], nodes.SimpleSelectorSequence)
                    anc = nodes.SimpleSelectorSequence(ancestors[-1].head, ancestors[-1].tail[:])  # clone()?
                    ancestors[-1] = anc
                    ancestors[-1].tail.extend(node.tail)
                newseq[i:i+1] = ancestors
                return newseq
        else:
            ancestors.append(nodes.DescendantCombinator())
            ancestors.extend(selector.children)
            return ancestors
    
    def resolve_selectors(self):
        selectors = []
        for selector_seq in self.selector_seqs:
            ancestors = []
            tail = selector_seq
            while tail:
                ancestors = self._resolve_selector(ancestors, tail[0])
                tail = tail[1:]
            sel = nodes.Selector(ancestors)
            selectors.append(sel)
        
        return selectors


#==============================================================================#
class RulesetFlattener(NodeTransformer):
    def __init__(self, options=None):
        pass
        
    def __call__(self, node):
        return self.visit(node)
    
    def visit(self, node):
        # All visits of RuleSets should be done by calling self.visit_RuleSet 
        # directly from their parent nodes.
        assert not isinstance(node, nodes.RuleSet)
        return super(RulesetFlattener, self).visit(node)
        
    def visit_Stylesheet(self, node):
        i = 0
        while i < len(node.statements):
            stmt = node.statements[i]
            if isinstance(stmt, nodes.RuleSet):
                # get chains from ruleset
                chains = self.visit_RuleSet(stmt)
                newrulesets = []
                for chain in chains:
                    # resolve chain selectors
                    selectors = chain.resolve_selectors()
                    statements = chain.statements
                    # create new ruleset from resolved selectors and statements
                    ruleset = nodes.RuleSet(selectors, statements)
                    newrulesets.append(ruleset)
                # replace stmt with new rulesets
                node.statements[i:i+1] = newrulesets
                i += len(newrulesets)
            else:
                newstmt = self.visit(stmt)
                if newstmt:
                    node.statements[i:i+1] = [newstmt]
                    i += 1
                else:
                    node.statements[i:i+1] = []
        return node
                
    def visit_RuleSet(self, node):
        child_rulesets = []
        child_statements = []  # non-ruleset statements
        for stmt in node.statements:
            if isinstance(stmt, nodes.RuleSet):
                child_rulesets.append(stmt)
            elif isinstance(stmt, nodes.VarDef):
                # TODO: use pkg-specific exception
                raise RuntimeError('Cannot flatten rulesets containing variable definitions.')
            else:
                child_statements.append(stmt)
        allchains = []
        for stmt in child_rulesets:
            chains = self.visit_RuleSet(stmt)
            allchains.extend(chains)
        for chain in allchains:
            chain.prepend_selectors(node.selectors)
        mychain = RulesetChain(node.selectors, child_statements)
        allchains.insert(0, mychain)
        assert all(isinstance(ch, RulesetChain) for ch in allchains)
        return allchains


#==============================================================================#

