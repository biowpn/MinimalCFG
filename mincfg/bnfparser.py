
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


def parse(src, long=False):
    rules = []

    nt_map = {}
    nt_count = 0
    special_char = ''
    lhs = None
    subs = []
    word = ""
    nt = None
    stack = []
    sub_nt = None

    for i, c in enumerate(src):
        if special_char in ('\"', '\''):
            if c == special_char:
                if not word:
                    subs.append('')
                else:
                    if long:
                        subs.append(word)
                    else:
                        subs.extend(word)
                word = ""
                special_char = ""
            else:
                word += c
            continue
        if c in ('\"', '\''):
            if special_char:
                raise ParsingException(f"unexpected {c}", src, i)
            special_char = c
        elif c == '<':
            if not special_char:
                word = ""
                special_char = c
            else:
                raise ParsingException(f"unexpected {c}", src, i)
        elif c == '>':
            if special_char == '<':
                if not word:
                    raise ParsingException(
                        f"non-terminal identifier cannot be empty", src, i)
                if word not in nt_map:
                    nt_map[word] = nt_count
                    nt_count += 1
                nt = nt_map[word]
                subs.append(nt)
                word = ""
                special_char = ""
            else:
                raise ParsingException(f"missing < for >", src, i)
        elif c == ':':
            if not special_char or special_char == ':':
                special_char += ':'
            else:
                raise ParsingException(f"unexpected {c}", src, i)
        elif c == '=':
            if special_char == "::":
                if lhs is None:
                    if len(subs) < 1:
                        raise ParsingException(
                            f"missing non-terminal before ::=", src, i)
                    lhs = subs.pop()
                else:
                    if len(subs) < 2:
                        raise ParsingException(
                            f"missing non-terminal before ::=", src, i)
                    rules.append((lhs, subs[:-1]))
                    lhs = subs.pop()
                if stack:
                    raise ParsingException("missing }", src, i)
                subs = []
                special_char = ""
            else:
                raise ParsingException(f"unexpected {c}", src, i)
        elif c == '|':
            if lhs is None:
                raise ParsingException(
                    f"missing left hand side before |", src, i)
            elif special_char:
                raise ParsingException(f"unexpected {c}", src, i)
            else:
                if len(subs) == 0:
                    raise ParsingException(
                        f"subsitution is empty before |", src, i)
                rules.append((lhs, subs))
                subs = []
        elif c == '{':
            stack.append((nt, subs))
            subs = []
        elif c == '}':
            if not stack:
                raise ParsingException("missing {", src, i)
            rules.append((nt_count, subs))
            sub_nt = nt_count
            nt_count += 1
        elif c == '?':
            if sub_nt is None:
                raise ParsingException(f"unexpected quantifier {c}", src, i)
            rules.append((nt_count, [""]))
            rules.append((nt_count, [sub_nt]))
            nt, subs = stack.pop()
            subs.append(nt_count)
            nt_count += 1
            sub_nt = None
        elif c == '*':
            if sub_nt is None:
                raise ParsingException(f"unexpected quantifier {c}", src, i)
            rules.append((nt_count, [""]))
            rules.append((nt_count, [sub_nt, nt_count]))
            nt, subs = stack.pop()
            subs.append(nt_count)
            nt_count += 1
            sub_nt = None
        elif c == '+':
            if sub_nt is None:
                raise ParsingException(f"unexpected quantifier {c}", src, i)
            rules.append((nt_count, [sub_nt]))
            rules.append((nt_count, [sub_nt, nt_count]))
            nt, subs = stack.pop()
            subs.append(nt_count)
            nt_count += 1
            sub_nt = None
        elif sub_nt is not None:
            raise ParsingException(
                "expected a quantifier following }", src, i)
        elif c in string.whitespace:
            pass
        else:
            if special_char == '<':
                word += c
            else:
                raise ParsingException(f"unexpected char '{c}'", src, i)

    if lhs is not None:
        if len(subs) > 0:
            rules.append((lhs, subs))
        else:
            raise ParsingException(
                "missing subsitution for the last rule", src, i)

    undefined_nts = set(nt_map.values()) - set([nt for nt, _ in rules])
    for nt_name, nt in nt_map.items():
        if nt in undefined_nts:
            print(
                f"warning: no production rule for non-terminal <{nt_name}> ({nt})")

    return rules, nt_map
