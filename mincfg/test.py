
from . import mincfg


def test_to_CNF():
    g1 = [
        (0, [0, 0]),
        (0, ['(', 0, ')']),
        (0, ['']),
    ]
    g1 = mincfg.to_cnf(g1)

    assert(len(g1) == 4)
    assert((0, [0, 0]) in g1)
    assert((0, ['(', 1]) in g1)
    assert((0, ['(', ')']) in g1)
    assert((1, [0, ')']) in g1)


def test_decide():
    # balanced parenthesis in CNF
    g1 = [
        (0, [0, 0]),
        (0, ['(', 1]),
        (0, ['(', ')']),
        (1, [0, ')'])
    ]

    assert(mincfg.decide(g1, "()") == True)
    assert(mincfg.decide(g1, "(())") == True)
    assert(mincfg.decide(g1, "(())()") == True)
    assert(mincfg.decide(g1, ")(") == False)
    assert(mincfg.decide(g1, "()(") == False)
    assert(mincfg.decide(g1, "())") == False)


def test_match_balanced_parenthesis():
    # balanced parenthesis, square brackets & curly brackets
    g1 = mincfg.compile("""
        <S> ::= <S> <S>
        <S> ::= '(' <S> ')'
        <S> ::= '[' <S> ']'
        <S> ::= '{' <S> '}'
        <S> ::= ''
    """)

    assert(g1.match("()") == True)
    assert(g1.match("[]") == True)
    assert(g1.match("{}") == True)
    assert(g1.match("()[]{}") == True)
    assert(g1.match("{()}") == True)
    assert(g1.match("{([])}") == True)
    assert(g1.match("()[{}]()") == True)
    assert(g1.match("(][)") == False)
    assert(g1.match("([)(])") == False)
    assert(g1.match("{([)]}") == False)


def test_match_simple_arithmetic_expression():
    # syntactically correct arithmetic expressions involing '+', '*', and parenthesis only
    g2 = mincfg.compile("""
        <E> ::= <E> '+' <T>
        <E> ::= <T>
        <T> ::= <T> '*' <F>
        <T> ::= <F>
        <F> ::= '(' <E> ')'
        <F> ::= 'x'
    """)

    assert(g2.match("") == False)
    assert(g2.match("x") == True)
    assert(g2.match("(x)") == True)
    assert(g2.match("x+x") == True)
    assert(g2.match("(x*x+x)*(x+x)") == True)

    assert(g2.match(")x(") == False)
    assert(g2.match("()") == False)
    assert(g2.match("x+") == False)
    assert(g2.match("(x*+x)*(x+x)") == False)


def test_match_arithmetic_expression():
    # syntactically correct integer arithmetic expressions
    g3 = mincfg.compile("""
        <E> ::= <ws> <E> <ws> '+' <ws> <T> <ws>
        <E> ::= <ws> <E> <ws> '-' <ws> <T> <ws>
        <E> ::= <T>
        <T> ::= <ws> <T> <ws> '*' <ws> <F> <ws>
        <T> ::= <ws> <T> <ws> '/' <ws> <F> <ws>
        <T> ::= <F>
        <F> ::= '(' <E> ')'
        <F> ::= <D>
        <D> ::= '-' <D>
        <D> ::= '0' <d>
        <D> ::= '1' <d>
        <D> ::= '2' <d>
        <D> ::= '3' <d>
        <D> ::= '4' <d>
        <D> ::= '5' <d>
        <D> ::= '6' <d>
        <D> ::= '7' <d>
        <D> ::= '8' <d>
        <D> ::= '9' <d>
        <d> ::= <D>
        <d> ::= ''
        <ws> ::= ' ' <ws>
        <ws> ::= ''
    """)

    assert(g3.match("(1)") == True)
    assert(g3.match("1+1") == True)
    assert(g3.match("1  + 1 ") == True)
    assert(g3.match("(-1)") == True)
    assert(g3.match("1 + -1") == True)
    assert(g3.match("1 + 2 * 3 - 4 / 2") == True)
    assert(g3.match("1 + 2 * (3 - 4) / -2") == True)
    assert(g3.match("(10 + 2) * (8 - 6)") == True)
    assert(g3.match("((3 + 20) / 5) - 4 * (8 + 9)") == True)

    assert(g3.match("1+") == False)
    assert(g3.match("1++1") == False)
    assert(g3.match("+ 3") == False)
    assert(g3.match("1 (+) 1") == False)
    assert(g3.match("(1 */ 5") == False)
    assert(g3.match("(1 + 3 * 5") == False)
    assert(g3.match("1 + 3) * 5") == False)
    assert(g3.match("4 * (13 - 2)) / 5") == False)


def test_match_simple_English():
    # a (very small) subset of English
    # references:
    #   https://en.wikipedia.org/wiki/English_grammar
    #   http://www.cs.uccs.edu/~jkalita/work/cs589/2010/12Grammars.pdf
    #   http://cs.union.edu/~striegnk/learn-prolog-now/html/node55.html
    g4 = mincfg.compile("""
        <English> ::= <English> <space> <Sentence> '.'
        <English> ::= <Sentence> '.'
        <Sentence> ::= <NounPhrase> <space> <VerbPhrase>
        <Sentence> ::= <Sentence> <space> <Conjunction> <space> <Sentence>
        <Sentence> ::= <Sentence> <space> <Conjunction> <space> <VerbPhrase>
        <space> ::= " " 

        <NounPhrase> ::= <Noun>
        <NounPhrase> ::= <Determiner> <space> <Noun>
        <NounPhrase> ::= <PronounSubj>

        <VerbPhrase> ::= <Verb>
        <VerbPhrase> ::= <Verb> <space> <NounPhrase>
        <VerbPhrase> ::= <Verb> <space> <PronounObj>

        <Noun> ::= <Adjective> <space> <Noun>

        <Determiner> ::= "the"
        <Determiner> ::= "a"

        <Conjunction> ::= "and"
        <Conjunction> ::= "so"

        <PronounSubj> ::= "I"
        <PronounSubj> ::= "she"

        <PronounObj> ::= "me"
        <PronounObj> ::= "her"

        <Verb> ::= "loved"
        <Verb> ::= "hated"
        <Verb> ::= "shot"
        <Verb> ::= "bought"
        <Verb> ::= "took"

        <Noun> ::= "gun"
        <Noun> ::= "python"

        <Adjective> ::= "lovely"
    """)

    assert(g4.match("I loved her. she loved me.") == True)
    assert(g4.match("I loved python.") == True)
    assert(g4.match("I bought a lovely python.") == True)
    assert(g4.match("she hated the python.") == True)
    assert(g4.match("she bought a gun and shot the python.") == True)
    assert(g4.match("I hated her.") == True)
    assert(g4.match("I took the gun and shot her.") == True)
    assert(g4.match("I feel sad.") == False)


def test_BNF_lexing():
    BNF = """
        <S> ::= "" | <A> <S> <B>
        <A> ::= "apple"
        <B> ::= "banana"
    """

    g = mincfg.compile(BNF, True)

    assert(g.match("apple banana") == True)
    assert(g.match("banana  apple") == False)
    assert(g.match("apple apple   banana") == False)
    assert(g.match(" apple apple  banana banana") == True)


def test_match_C_programming_language():
    with open("examples/c99.bnf") as F:
        g6 = mincfg.compile(F.read(), True)
    print("number of rules of this mincfg in CNF:", len(g6.grammar))

    # function declaration
    assert(g6.match("int main(){return 0;}") == True)
    assert(g6.match("int main({return 0;}") == False)
    assert(g6.match("int main(){return 0};") == False)
    assert(g6.match("int main(int id1, char** id2){return 0;}") == True)
    assert(g6.match("int main(id1, id2){return 0};") == False)

    # conditional statement
    assert(
        g6.match("int id0(int id1, int id2){return id1 > id2 ? id1 : id2;}") == True)
    assert(g6.match(
        "int id0(int id1, int id2){if (id1 > id2) {return id1;} else {return id2;} }") == True)

    # loop
    assert(g6.match(
        "int id0(int id1){int id2 = 0; for(;id1 > 0;--id1) id2 += id1; return id2;}") == True)
    assert(g6.match(
        "int id0(int id1){int id2 = 0; while(id1 > 0) id2 += id1--; return id2;}") == True)

    # struct definition
    assert(g6.match("struct id0;") == True)
    assert(g6.match("struct id0{int id1; double id2; char id3[4];};") == True)
    assert(
        g6.match("struct id0(){int id1; double id2; char id3[4];};") == False)

    # pointer
    assert(
        g6.match("void id0(){ int id1; int* id2; id2 = &id1; *id2 = 0; }") == True)


def main():
    for name, func in globals().items():
        if name.startswith("test_") and callable(func):
            func()
            print(f"{name} passed")
    print("all passed")


if __name__ == "__main__":
    main()
