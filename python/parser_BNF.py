
'''
Backus–Naur Form CFG notation

https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form

example:
    <DNA> ::= <DNA> <Nucleotide> | <Nucleotide>
    <Nucleotide> ::= 'A' | 'G' | 'C' | 'T'
'''

import string


class ParsingException(Exception):

    def __init__(self, desc, fulltxt, pos):
        self.fulldesc = "\n"
        lines = fulltxt.split('\n')
        for i, line in enumerate(lines):
            if pos < len(line):
                line_prefix = f"Line {i + 1}: "
                self.fulldesc += line_prefix + line + '\n'
                self.fulldesc += ' ' * (len(line_prefix) + pos) + '^' + '\n'
                self.fulldesc += desc
                break
            pos -= len(line) + 1

    def __str__(self):
        return self.fulldesc


def parse(cfgex):
    G_out = []

    nt_idx = {}
    special_char = ''
    lhs = None
    subs = []
    word = ""
    nt = None

    for i, c in enumerate(cfgex):
        if c == '<':
            if special_char in ('\"', '\''):
                word += c
            elif not special_char:
                word = ""
                special_char = c
            else:
                raise ParsingException(f"Unexpected {c}", cfgex, i)
        elif c == '>':
            if special_char in ('\"', '\''):
                word += c
            elif special_char == '<':
                if not word:
                    raise ParsingException(
                        f"non-terminal identifier cannot be empty", cfgex, i)
                nt_idx[word] = nt_idx.get(word, len(nt_idx))
                if nt is not None:
                    subs.append(nt)
                nt = nt_idx[word]
                word = ""
                special_char = ""
            else:
                raise ParsingException(f"Missing < for >", cfgex, i)
        elif c == ':':
            if special_char in ('\"', '\''):
                word += c
            elif not special_char or special_char == ':':
                special_char += ':'
            else:
                raise ParsingException(f"Unexpected {c}", cfgex, i)
        elif c == '=':
            if special_char in ('\"', '\''):
                word += c
            elif special_char == "::":
                if nt is None:
                    raise ParsingException(
                        f"missing non-terminal before ::=", cfgex, i)
                if lhs and subs:
                    G_out.append((lhs, subs))
                lhs = nt
                subs = []
                nt = None
                special_char = ""
            else:
                raise ParsingException(f"Unexpected {c}", cfgex, i)
        elif c == '|':
            if special_char in ('\"', '\''):
                word += c
            elif lhs is None:
                raise ParsingException(
                    f"missing left hand side before |", cfgex, i)
            elif special_char:
                raise ParsingException(f"Unexpected {c}", cfgex, i)
            else:
                if nt is not None:
                    subs.append(nt)
                if len(subs) == 0:
                    raise ParsingException(
                        f"subsitution is empty before |", cfgex, i)
                G_out.append((lhs, subs))
                subs = []
                nt = None
        elif c in ('\"', '\''):
            if special_char == c:
                if not word:
                    subs.append('')
                else:
                    subs.extend(word)
                word = ""
                special_char = ""
            elif special_char in ('\"', '\''):
                word += c
            elif not special_char:
                special_char = c
            else:
                raise ParsingException(f"Unexpected {c}", cfgex, i)
        else:
            if special_char in ('\"', '\'', '<'):
                word += c
            elif c in string.whitespace:
                pass
            else:
                raise ParsingException(f"Unexpected char '{c}'", cfgex, i)

    if lhs is not None:
        if nt is not None:
            subs.append(nt)
        if len(subs) > 0:
            G_out.append((lhs, subs))
        else:
            raise ParsingException(
                "missing subsitution for the last rule", cfgex, i)
    
    undefined_nts = set(nt_idx.values()) - set([nt for nt, _ in G_out])
    for nt_name, nt in nt_idx.items():
        if nt in undefined_nts:
            print(f"Warning: no production rule for non-terminal <{nt_name}>")

    return G_out
