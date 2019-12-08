

def match(cfgex, string):
    '''
    given a Context-Free Grammar expression @cfgex, decide whether @string can be produced by it.
    '''
    recognizer = compile(cfgex)
    return recognizer.match(string)


def compile(cfgex):
    '''
    parse expression @cfgex and convert the resulted Context-Free Grammar it into Chomsky Normal Form.
    '''
    return CFLRecognizer(cfgex)


def parse(cfgex):
    '''
    convert expression @cfgex to structured Context-Free Grammar.

    @cfgex should satisfy the following format requirements:
        1. rules are seperated by ';'
        2. for each rule, nonterminal and subsitutions are seperated by ':'
        3. nonterminals are identified by names surrounded by '{' and '}'
        4. white spaces are taken into account
        5. to indicate literal '{', '}', ':' or ';', add a '\' before them
        6. to indicate literal '\', use '\\'
    an example:
        S:a{S}a;S:b{S}b;S:;
    '''
    G_out = []

    nt_idx = {}
    escaped = False
    open_curly = False
    stage = 0
    nt = ""
    subs = []
    symbol = ""
    for c in cfgex:
        if c == '\\':
            if escaped:
                subs.append(c)
                escaped = False
            else:
                if stage == 0:
                    raise Exception(
                        "cannot escape on the left hand side of a rule")
                if open_curly:
                    raise Exception(
                        "non-terminal identifier does not contain special symbols")
                escaped = True
        elif c == '{':
            if escaped:
                subs.append(c)
                escaped = False
            else:
                if open_curly:
                    raise Exception(
                        "previous open curly brace hasn't been closed")
                if stage == 1:
                    raise Exception(
                        "already specified a non-terminal identifier")
                symbol = ""
                open_curly = True
        elif c == '}':
            if escaped:
                subs.append(c)
                escaped = False
            else:
                if open_curly:
                    if not symbol:
                        raise Exception(
                            "non-terminal identifier cannot be empty")
                    if stage == 0:
                        stage == 1
                    elif stage == 1:
                        raise Exception("impossible stage 1")
                    else:
                        nt_idx[symbol] = nt_idx.get(symbol, len(nt_idx))
                        subs.append(nt_idx[symbol])
                    open_curly = False
                else:
                    raise Exception("missing open curly brace")
        elif c == ':':
            if escaped:
                subs.append(c)
                escaped = False
            else:
                if stage == 2:
                    raise Exception("unexpected ':'")
                nt_idx[symbol] = nt_idx.get(symbol, len(nt_idx))
                nt = nt_idx[symbol]
                stage = 2
                subs = []
        elif c == ';':
            if escaped:
                subs.append(c)
                escaped = False
            else:
                if stage != 2:
                    raise Exception("unexpected ';'")
                if len(subs) == 0:
                    subs = ['']
                G_out.append((nt, subs))
                stage = 0
                symbol = ""
        else:
            if open_curly or stage == 0:
                symbol += c
            elif stage == 1:
                raise Exception("expecting a ':'")
            else:
                subs.append(c)

    return G_out


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
    return G_out + G_out_extra


def to_CNF(G):
    '''
    convert CFG @G to Chomsky Normal Form.
    '''
    G = eliminate_long_rules(G)
    G = eliminate_e_rules(G)
    G = eliminate_short_rules(G)
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

    def __init__(self, cfgex):
        self.G = parse(cfgex)
        self.G = to_CNF(self.G)

    def match(self, string):
        return decide(self.G, string)
