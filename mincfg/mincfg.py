
import bnfparser
from . import lexer


def match(cfgex, string, lexing=False):
    '''
    given a Context-Free Grammar expression `cfgex`, decide whether `string` can be produced by it.
    `lexing` if True, will preserve long terminals.
    '''
    recognizer = compile(cfgex, lexing)
    return recognizer.match(string)


def compile(cfgex, lexing=False):
    '''
    parse expression `cfgex` and convert the resulted Context-Free Grammar it into Chomsky Normal Form.
    `lexing` if True, will preserve long terminals.
    '''
    return CFLRecognizer(cfgex, lexing)


def parse(cfgex, lexing=False):
    lexemes = bnfparser.lexer.lex(cfgex, lexing)
    bp = bnfparser.BNFParser()
    return bp.parse(lexemes)


def get_min_non_terminal(G):
    return min(nt for nt, _ in G)


def eliminate_long_rules(G):
    '''
    break down long rule:
        A -> B1 B2 B3 B4
    to short rules:
        A -> B1 A1
        A1 -> B2 A2
        A2 -> B3 B4
    '''
    nt_new = get_min_non_terminal(G) - 1
    G_out = []
    for nt, subs in G:
        if len(subs) > 2:
            G_out.append((nt, [subs[0], nt_new]))
            for a in subs[1:-2]:
                G_out.append((nt_new, [a, nt_new - 1]))
                nt_new -= 1
            G_out.append((nt_new, subs[-2:]))
            nt_new -= 1
        else:
            G_out.append((nt, subs))
    return G_out


def reverse_closure(G, s):
    '''
    get the set of nonterminals that may derive symbol `s` via some short rules
    '''
    nt_s = {s}
    done = False
    while not done:
        done = True
        for nt, subs in G:
            if len(subs) == 1 and subs[0] in nt_s and nt not in nt_s:
                nt_s.add(nt)
                done = False
    nt_s.remove(s)
    return nt_s


def reverse_closure_e(G):
    '''
    get the set of nonterminals that may derive empty string ''
    '''
    nt_s = {''}
    done = False
    while not done:
        done = True
        for nt, subs in G:
            if all([s in nt_s for s in subs]) and nt not in nt_s:
                nt_s.add(nt)
                done = False
    nt_s.remove('')
    return nt_s


def eliminate_e_rules(G):
    '''
    e-rules:
        A -> ''
    assuming long rules have been eliminated.
    '''
    grammar = []
    e = reverse_closure_e(G)

    for nt, subs in G:
        if len(subs) == 1:
            if subs[0] != '':
                grammar.append((nt, subs))
        elif len(subs) == 2:
            if subs[0] in e and nt != subs[1]:
                grammar.append((nt, [subs[1]]))
            if subs[1] in e and nt != subs[0]:
                grammar.append((nt, [subs[0]]))
            grammar.append((nt, subs))
    return grammar


def closure_s(G, s):
    '''
    get the set of symbols that may be derived from non-terminal `s` by some short rule.
    '''
    d = {s}
    if type(s) is str:
        return d
    done = False
    while not done:
        done = True
        for nt, subs in G:
            if len(subs) == 1 and nt in d and subs[0] not in d:
                d.add(subs[0])
                done = False
    return d


def eliminate_short_rules(G):
    '''
    short rules:
        A -> B
    assuming long rules and e-rules have been eliminated.
    assuming starting non-terminal is -1.
    '''
    grammar = []
    d_s = {}  # key: symbol; value: its short-rule closures
    d_s[0] = closure_s(G, -1)
    for nt, subs in G:
        if len(subs) == 2:
            a, b = subs
            if a not in d_s:
                d_s[a] = closure_s(G, a)
            if b not in d_s:
                d_s[b] = closure_s(G, b)
            for a_ in d_s[a]:
                for b_ in d_s[b]:
                    grammar.append((nt, [a_, b_]))

    grammar_extra = []
    for a in d_s[0] - {-1}:
        for nt, subs in grammar:
            if nt == a and len(subs) == 2:
                grammar_extra.append((-1, subs))
    grammar = grammar + grammar_extra

    return grammar


def minimize_rules_1(G):
    '''
    Perform the following (trivial) minimization:
        - remove duplicated rules
        - remove self-produced rule
    '''

    # remove duplicated rules
    G2 = []
    for rule1 in G:
        duplicated = False
        for rule2 in G2:
            if rule1[0] == rule2[0] and rule1[1] == rule2[1]:
                duplicated = True
                break
        if not duplicated:
            G2.append(rule1)
    G = G2

    # remove self-produced rule
    G2 = []
    for nt, sub in G:
        if len(sub) == 1 and nt == sub[0]:
            continue
        G2.append((nt, sub))
    G = G2

    return G


def minimize_rules_2(G):
    '''
    Perform the following minimization:
        - remove production rules containing undefined non-terminals
    '''
    # remove production rules containing undefined non-terminals
    G2 = []
    nt_s = set()
    defined_nt_s = set()
    for nt, subs in G:
        defined_nt_s.add(nt)
        for s in subs:
            if type(s) is int:
                nt_s.add(s)
    undefined_nt_s = nt_s - defined_nt_s
    for nt, subs in G:
        if all(s not in undefined_nt_s for s in subs):
            G2.append((nt, subs))
    G = G2

    return G


def minimize_rules_3(G):
    '''
    Perform the following minimization:
        - remove non-terminal produced by exactly one short rule

            For example:
                <a> ::= <x>
                <x> ::= '0'
                <x> ::= '1'
            We can then eliminate <x>, resulting:
                <a> ::= '0'
                <a> ::= '1'

            Note that if the non-terminal can be produced by more than one short rules,
            there is no benefit in eliminating it:
                <a> ::= <x>
                <b> ::= <x>
                <c> ::= <x>
                <x> ::= '0'
                <x> ::= '1'
            Eliminating <x> would result in a total of 6 rules, even more than before!

            Also, we never eliminate the starting -1 non-terminal.

    Assuming there are short rules.
    '''

    nt_s = set(nt for nt, _ in G)
    done = False
    while not done:
        done = True
        for nt in nt_s:
            nt0 = None
            by_short_rule_count = 0
            for nt2, sub in G:
                if len(sub) > 1 and nt in sub:
                    by_short_rule_count = -1
                    break
                if len(sub) == 1 and sub[0] == nt:
                    by_short_rule_count += 1
                    nt0 = nt2
            if by_short_rule_count == 1:
                # now we eliminate nt
                G2 = []
                for nt2, sub in G:
                    if len(sub) == 1 and sub[0] == nt:
                        continue
                    if nt2 == nt:
                        # replace it by the non-terminal that produces it
                        nt2 = nt0
                    G2.append((nt2, sub))
                G = G2
                nt_s.remove(nt)
                done = False
                break

    return G


def to_cnf(G):
    '''
    convert CFG `G` to Chomsky Normal Form.
    '''

    # print(f"before minimize, n = {len(G)}")
    G = minimize_rules_1(G)
    G = minimize_rules_2(G)
    # print(f"after minimize, n = {len(G)}")

    G = eliminate_long_rules(G)

    G = eliminate_e_rules(G)

    # print(f"before minimize, n = {len(G)}")
    G = minimize_rules_3(G)
    # print(f"after minimize, n = {len(G)}")

    G = eliminate_short_rules(G)

    # print(f"before minimize, n = {len(G)}")
    G = minimize_rules_2(G)
    # print(f"after minimize, n = {len(G)}")

    return G


def decide(G, x):
    '''
    given CFG `G` in CNF, decide if string `x` is in L(G).
    '''
    n = len(x)
    if n < 2:
        raise Exception("string must be at least two-character-long")

    # N[i][j] is the set of all symbols that can derive substring x[i:j+1]
    N = [[set() for _ in range(n)] for _ in range(n)]

    # initialize N
    for i in range(n):
        N[i][i] = {x[i]}

    # dynamic programming loop
    for s in range(1, n):
        # s = the length of the substring - 1
        for i in range(n - s):
            # i is the starting index of the substring
            # (i + s) is the ending index of the substring
            for k in range(i, i + s):
                # substring is divided by two halves: first half + second half
                # k is the ending index of the first half
                for a, (b, c) in G:
                    if b in N[i][k] and c in N[k + 1][i + s]:
                        N[i][i + s].add(a)

    # assume starting state is -1
    return -1 in N[0][n - 1]


class CFLRecognizer:

    def __init__(self, cfgex, lexing):
        self.lexing = lexing
        self.grammar = parse(cfgex, lexing)
        self.grammar_cnf = to_cnf(self.grammar)

    def match(self, string):
        if len(string) == 0:
            return self._match_len0()
        elif len(string) == 1:
            return self._match_len1(string[0])

        if self.lexing:
            string = lexer.lex(self.grammar_cnf, string)
            print("post lexing:", string)
        return decide(self.grammar_cnf, string)

    def _match_len0(self):
        nt_s = reverse_closure_e(self.grammar)
        return -1 in nt_s

    def _match_len1(self, s):
        G = minimize_rules_1(self.grammar)
        G = eliminate_long_rules(G)
        G = eliminate_e_rules(G)
        nt_s = reverse_closure(G, s)
        return -1 in nt_s
