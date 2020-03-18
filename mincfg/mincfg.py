
from . import bnfparser
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
    return bnfparser.parse(cfgex, lexing)[0]


def get_max_non_terminal(G):
    nt_max = 0
    for nt, _ in G:
        if nt > nt_max:
            nt_max = nt
    return nt_max


def eliminate_long_rules(G):
    '''
    break down long rule:
        A -> B1 B2 B3 B4
    to short rules:
        A -> B1 A1
        A1 -> B2 A2
        A2 -> B3 B4
    '''
    nt_new = get_max_non_terminal(G) + 1
    G_out = []
    for nt, subs in G:
        if len(subs) > 2:
            G_out.append((nt, [subs[0], nt_new]))
            for a in subs[1:-2]:
                G_out.append((nt_new, [a, nt_new + 1]))
                nt_new += 1
            G_out.append((nt_new, subs[-2:]))
            nt_new += 1
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
    '''
    grammar = []
    d_s = {}  # key: symbol; value: its short-rule closures
    d_s[0] = closure_s(G, 0)
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
    for a in d_s[0] - {0}:
        for nt, subs in grammar:
            if nt == a and len(subs) == 2:
                grammar_extra.append((0, subs))
    grammar = grammar + grammar_extra

    return grammar


def minimize_rules(G):
    '''
    perform the following minimization:
        - remove production rules containing undefined non-terminals
        - replace terminals that have a single short production rule
    '''
    grammar_defined = []
    nt_s = set()
    defined_nt_s = set()
    for nt, subs in G:
        defined_nt_s.add(nt)
        for s in subs:
            if type(s) is int:
                nt_s.add(s)
    undefined_nt_s = nt_s - defined_nt_s
    for nt, subs in G:
        if all([s not in undefined_nt_s for s in subs]):
            grammar_defined.append((nt, subs))
    nt_s = nt_s - undefined_nt_s

    grammar_non_single = grammar_defined

    # TODO: the following logic below may not preserve equivalent grammar
    # while True:
    #     G_wip = []
    #     non_single_nt_s = set()
    #     single_nt_s = {}
    #     for nt, subs in G_non_single:
    #         if len(subs) == 1:
    #             if nt in non_single_nt_s:
    #                 continue
    #             elif nt in single_nt_s and subs[0] != single_nt_s[nt]:
    #                 single_nt_s.pop(nt)
    #                 non_single_nt_s.add(nt)
    #             else:
    #                 single_nt_s[nt] = subs[0]
    #         else:
    #             non_single_nt_s.add(nt)
    #             if nt in single_nt_s:
    #                 single_nt_s.pop(nt)
    #     if 0 in single_nt_s:
    #         single_nt_s.pop(0)
    #     if not single_nt_s:
    #         break
    #     for nt, subs in G_non_single:
    #         if nt in single_nt_s:
    #             continue
    #         for i, s in enumerate(subs):
    #             if s in single_nt_s:
    #                 subs[i] = single_nt_s[s]
    #         G_wip.append((nt, subs))
    #     G_non_single = G_wip

    return grammar_non_single


def to_cnf(g):
    '''
    convert CFG `g` to Chomsky Normal Form.
    '''
    g = minimize_rules(g)
    g = eliminate_long_rules(g)
    g = eliminate_e_rules(g)
    g = eliminate_short_rules(g)
    g = minimize_rules(g)
    return g


def decide(g, x):
    '''
    given CFG `g` in CNF, decide if string `x` is in L(g).
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
                for a, (b, c) in g:
                    if b in N[i][k] and c in N[k + 1][i + s]:
                        N[i][i + s].add(a)

    # assume starting state is 0
    return 0 in N[0][n - 1]


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
        return 0 in nt_s

    def _match_len1(self, s):
        g = minimize_rules(self.grammar)
        g = eliminate_long_rules(g)
        g = eliminate_e_rules(g)
        nt_s = reverse_closure(g, s)
        return 0 in nt_s
