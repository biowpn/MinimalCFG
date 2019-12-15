
import string


class ParsingException(Exception):

    def __init__(self, desc, fulltxt, pos):
        self.fulldesc = "\n"
        lines = fulltxt.split('\n')
        for i, line in enumerate(lines):
            if pos < len(line):
                line_prefix = f"line {i + 1}: "
                self.fulldesc += line_prefix + line + '\n'
                self.fulldesc += ' ' * (len(line_prefix) + pos) + '^' + '\n'
                self.fulldesc += desc
                break
            pos -= len(line) + 1

    def __str__(self):
        return self.fulldesc


def lex(G, x):
    '''
    break down string @x into terminals given CFG @G.
    '''
    terminals = set()
    for nt, subs in G:
        for s in subs:
            if type(s) is str:
                terminals.add(s)
    lexer = Lexer(terminals)
    return lexer.analyze(x)


class Lexer:

    def __init__(self, tokens):
        self.tokens = {}
        for tk in tokens:
            s = len(tk)
            if s not in self.tokens:
                self.tokens[s] = []
            self.tokens[s].append(tk)
        self.token_lengths = sorted(self.tokens.keys(), reverse=True)

    def analyze(self, input_str):
        out = []

        i = 0
        while i < len(input_str):
            if input_str[i] in string.whitespace:
                i += 1
                continue
            matched = False
            for s in self.token_lengths:
                ptk = input_str[i: i + s]
                for tk in self.tokens[s]:
                    if tk == ptk:
                        out.append(ptk)
                        i += s
                        matched = True
                        break
                if matched:
                    break
            if not matched:
                raise ParsingException("unknown token", input_str, i)

        return out
