
'''
Minimal-style CFG notation

1. production rules are seperated by ';'
2. for each rule, nonterminal and subsitutions are seperated by ':'
3. nonterminals are identified by names surrounded by '{' and '}'
4. white spaces between ':' and ';' are taken into account
5. to indicate literal '{', '}', ':', ';', or '\\', add a '\' before them

example:
    S:a{S}a;S:b{S}b;S:;
'''


def parse(cfgex):
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
