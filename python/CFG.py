
import lexer
import parser_Minimal
import parser_BNF


def match(cfgex, string, fmt='Minimal', lexing=False):
    '''
    given a Context-Free Grammar expression @cfgex, decide whether @string can be produced by it.
    @fmt format of the CFG notation. support 'Minimal', 'BNF'
    @lexing (for BNF) if True, will preserve long string terminals and use lexer.
    '''
    recognizer = compile(cfgex, fmt, lexing)
    return recognizer.match(string)


def compile(cfgex, fmt='Minimal', lexing=False):
    '''
    parse expression @cfgex and convert the resulted Context-Free Grammar it into Chomsky Normal Form.
    @fmt format of the CFG notation. support 'Minimal', 'BNF'
    @lexing (for BNF) if True, will preserve long string terminals and use lexer.
    '''
    return CFLRecognizer(cfgex, fmt, lexing)


def parse(cfgex, fmt='Minimal', lexing=False):
    if fmt == 'Minimal':
        return parser_Minimal.parse(cfgex)
    elif fmt == 'BNF':
        return parser_BNF.parse(cfgex, lexing)
    else:
        raise Exception(f"Unsupported CFG format: {fmt}")


def get_max_non_terminal(G):
    nt_max = 0
    for nt, subs in G:
        if nt > nt_max:
            nt_max = nt
    return nt_max


def eliminate_long_rules(G):
    '''
    break down
        A -> B1 B2 B3 B4
    to
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


def closure_e(G):
    '''
    get the set of nonterminals that may derive ''
    '''
    E = {''}
    done = False
    while not done:
        done = True
        for nt, subs in G:
            if all([s in E for s in subs]) and nt not in E:
                E.add(nt)
                done = False
    E.remove('')
    return E


def eliminate_e_rules(G):
    '''
    e-rules:
        A -> ''
    assuming long rules have been eliminated.
    '''
    G_out = []
    E = closure_e(G)

    for nt, subs in G:
        if len(subs) == 1:
            if subs[0] != '':
                G_out.append((nt, subs))
        elif len(subs) == 2:
            if subs[0] in E and nt != subs[1]:
                G_out.append((nt, [subs[1]]))
            if subs[1] in E and nt != subs[0]:
                G_out.append((nt, [subs[0]]))
            G_out.append((nt, subs))
    return G_out


def closure_s(G, s):
    '''
    get the set of symbols that may derive from @s by some short rule.
    '''
    D = {s}
    if type(s) is str:
        return D
    done = False
    while not done:
        done = True
        for nt, subs in G:
            if len(subs) == 1 and nt in D and subs[0] not in D:
                D.add(subs[0])
                done = False
    return D


def eliminate_short_rules(G):
    '''
    short rules:
        A -> B
    assuming long rules and e-rules have been eliminated.
    '''
    G_out = []
    Ds = {}  # key: symbol; value: its short-rule closures
    Ds[0] = closure_s(G, 0)
    for nt, subs in G:
        if len(subs) == 2:
            a, b = subs
            if a not in Ds:
                Ds[a] = closure_s(G, a)
            if b not in Ds:
                Ds[b] = closure_s(G, b)
            for a_ in Ds[a]:
                for b_ in Ds[b]:
                    G_out.append((nt, [a_, b_]))

    G_out_extra = []
    for a in Ds[0] - {0}:
        for nt, subs in G_out:
            if nt == a and len(subs) == 2:
                G_out_extra.append((0, subs))
    G_out = G_out + G_out_extra

    return G_out


def minimize_rules(G):
    '''
    perform the following minimization:
        - remove production rules containing undefined non-terminals
        - replace terminals that have a single short production rule
    '''
    G_all_defined = []
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
            G_all_defined.append((nt, subs))
    nt_s = nt_s - undefined_nt_s

    G_non_single = G_all_defined

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

    return G_non_single


def to_CNF(G):
    '''
    convert CFG @G to Chomsky Normal Form.
    '''
    G = minimize_rules(G)
    G = eliminate_long_rules(G)
    G = eliminate_e_rules(G)
    G = eliminate_short_rules(G)
    G = minimize_rules(G)
    return G


def decide(G, x):
    '''
    given CFG @G in CNF, decide if string @x is in L(G).
    '''
    n = len(x)
    if n < 1:
        raise Exception("empty string not support")

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

    # assume starting state is 0
    return 0 in N[0][n - 1]


class CFLRecognizer:

    def __init__(self, cfgex, fmt, lexing):
        self.lexing = lexing
        self.G = parse(cfgex, fmt, lexing)
        self.G = to_CNF(self.G)

    def match(self, string):
        if self.lexing:
            string = lexer.lex(self.G, string)
            print("post lexing:", string)
        return decide(self.G, string)
