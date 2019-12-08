
import CFG


def test_parse():
    G1 = CFG.parse(r"S:{S}{S};S:();S:;")

    # this should also work, and be equilvalent to G1
    G2 = CFG.parse(r"""
        {S}:{S}{S};
        {S}:();
        {S}:;
    """)

    assert(G1 == G2)


def test_to_CNF():
    G1 = [
        (0, [0, 0]),
        (0, ['(', 0, ')']),
        (0, ['']),
    ]
    G1 = CFG.to_CNF(G1)

    assert(len(G1) == 4)
    assert((0, [0, 0]) in G1)
    assert((0, ['(', 1]) in G1)
    assert((0, ['(', ')']) in G1)
    assert((1, [0, ')']) in G1)


def test_decide():
    # balanced parenthesis in CNF
    G1 = [
        (0, [0, 0]),
        (0, ['(', 1]),
        (0, ['(', ')']),
        (1, [0, ')'])
    ]

    assert(CFG.decide(G1, "()") == True)
    assert(CFG.decide(G1, "(())") == True)
    assert(CFG.decide(G1, "(())()") == True)
    assert(CFG.decide(G1, ")(") == False)
    assert(CFG.decide(G1, "()(") == False)
    assert(CFG.decide(G1, "())") == False)


def test_match_balanced_parenthesis():
    # balanced parenthesis, square brackets & curly brackets
    G1 = CFG.compile(r"""
        {S}:{S}{S};
        {S}:({S});
        {S}:[{S}];
        {S}:\{{S}\};
        {S}:;
    """)

    assert(G1.match("()") == True)
    assert(G1.match("[]") == True)
    assert(G1.match("{}") == True)
    assert(G1.match("()[]{}") == True)
    assert(G1.match("{()}") == True)
    assert(G1.match("{([])}") == True)
    assert(G1.match("()[{}]()") == True)
    assert(G1.match("(][)") == False)
    assert(G1.match("([)(])") == False)
    assert(G1.match("{([)]}") == False)


def test_match_simple_arithmetic_expression():
    # syntactically correct arithmetic expressions involing '+', '*', and parenthesis only
    G2 = CFG.compile(r"""
        {E}:{E}+{T};
        {E}:{T};
        {T}:{T}*{F};
        {T}:{F};
        {F}:({E});
        {F}:id;
    """)

    assert(G2.match("id") == True)
    assert(G2.match("(id)") == True)
    assert(G2.match("id+id") == True)
    assert(G2.match("(id*id+id)*(id+id)") == True)

    assert(G2.match(")id(") == False)
    assert(G2.match("()") == False)
    assert(G2.match("id+") == False)
    assert(G2.match("(id*+id)*(id+id)") == False)


def test_match_arithmetic_expression():
    # syntactically correct integer arithmetic expressions
    G3 = CFG.compile(r"""
        {E}:{ws}{E}{ws}+{ws}{T}{ws};
        {E}:{ws}{E}{ws}-{ws}{T}{ws};
        {E}:{T};
        {T}:{ws}{T}{ws}*{ws}{F}{ws};
        {T}:{ws}{T}{ws}/{ws}{F}{ws};
        {T}:{F};
        {F}:({E});
        {F}:{D};
        {D}:-{D};
        {D}:0{d};
        {D}:1{d};
        {D}:2{d};
        {D}:3{d};
        {D}:4{d};
        {D}:5{d};
        {D}:6{d};
        {D}:7{d};
        {D}:8{d};
        {D}:9{d};
        {d}:{D};
        {d}:;
        {ws}: {ws};
        {ws}:;
    """)

    assert(G3.match("(1)") == True)
    assert(G3.match("1+1") == True)
    assert(G3.match("1  + 1 ") == True)
    assert(G3.match("(-1)") == True)
    assert(G3.match("1 + -1") == True)
    assert(G3.match("1 + 2 * 3 - 4 / 2") == True)
    assert(G3.match("1 + 2 * (3 - 4) / -2") == True)
    assert(G3.match("(10 + 2) * (8 - 6)") == True)
    assert(G3.match("((3 + 20) / 5) - 4 * (8 + 9)") == True)

    assert(G3.match("1+") == False)
    assert(G3.match("1++1") == False)
    assert(G3.match("+ 3") == False)
    assert(G3.match("1 (+) 1") == False)
    assert(G3.match("(1 */ 5") == False)
    assert(G3.match("(1 + 3 * 5") == False)
    assert(G3.match("1 + 3) * 5") == False)
    assert(G3.match("4 * (13 - 2)) / 5") == False)


def test_match_simple_English():
    # a (very small) subset of English
    # references:
    #   https://en.wikipedia.org/wiki/English_grammar
    #   http://www.cs.uccs.edu/~jkalita/work/cs589/2010/12Grammars.pdf
    #   http://cs.union.edu/~striegnk/learn-prolog-now/html/node55.html
    G4 = CFG.compile(r"""
        {English}:{English}{space}{Sentence}.;
        {English}:{Sentence}.;
        {Sentence}:{NounPhrase}{space}{VerbPhrase};
        {Sentence}:{Sentence}{space}{Conjunction}{space}{Sentence};
        {Sentence}:{Sentence}{space}{Conjunction}{space}{VerbPhrase};
        {space}: ;

        {NounPhrase}:{Noun};
        {NounPhrase}:{Determiner}{space}{Noun};
        {NounPhrase}:{PronounSubj};

        {VerbPhrase}:{Verb};
        {VerbPhrase}:{Verb}{space}{NounPhrase};
        {VerbPhrase}:{Verb}{space}{PronounObj};

        {Noun}:{Adjective}{space}{Noun};

        {Determiner}:the;
        {Determiner}:a;

        {Conjunction}:and;
        {Conjunction}:so;

        {PronounSubj}:I;
        {PronounSubj}:she;

        {PronounObj}:me;
        {PronounObj}:her;

        {Verb}:loved;
        {Verb}:hated;
        {Verb}:shot;
        {Verb}:bought;
        {Verb}:took;

        {Noun}:gun;
        {Noun}:python;

        {Adjective}:lovely;
    """)

    assert(G4.match("I loved her. she loved me.") == True)
    assert(G4.match("I loved python.") == True)
    assert(G4.match("I bought a lovely python.") == True)
    assert(G4.match("she hated the python.") == True)
    assert(G4.match("she bought a gun and shot the python.") == True)
    assert(G4.match("I hated her.") == True)
    assert(G4.match("I took the gun and shot her.") == True)
    assert(G4.match("I feel sad.") == False)


def test_match_CFG_expression():
    # check whether the expression is a valid CFG expression within this project.
    # such CFG can even test itself!

    #   e   CFG expression
    #   r   rule
    #   n   non-terminal
    #   s   subsitution
    #   a   ascii letters
    #   d   digits
    #   w   whitespace
    #   p   punctuations
    CFGex = r"""
        {e}:{w}{e}{w};
        {e}:{e}{r};
        {e}:{r};
        {r}:{n}\:{s}\;;
        {r}:\{{n}\}\:{s}\;;
        {n}:;
        {n}:{a}{n};
        {s}:;
        {s}:{a}{s};
        {s}:{d}{s};
        {s}:{p}{s};
        {s}:{w}{s};
        {s}:\{{n}\}{s};
    """
    import string
    for a in string.ascii_letters:
        CFGex += "{a}:" + a + ";"
    for d in string.digits:
        CFGex += "{d}:" + d + ";"
    for w in string.whitespace:
        CFGex += "{w}:" + w + ";"
    for p in string.punctuation:
        if p in ['{', '}', ':', ';', '\\']:
            p = '\\' * 3 + p
        CFGex += "{p}:" + p + ';'

    G5 = CFG.compile(CFGex)
    print("number of rules of this CFG in CNF:", len(G5.G))

    # from early example: match_balanced_parenthesis
    assert(G5.match(r"S:{S}{S};S:();S:;") == True)

    # for the self-testing, it takes A LOT of time to run,
    # because both the grammar size and input string are large.
    # I never finish it.

    # assert(G5.match(CFGex) == True)


def main():
    for name, func in globals().items():
        if name.startswith("test_") and callable(func):
            func()
            print(f"{name} passed")
    print("all passed")


if __name__ == "__main__":
    main()
