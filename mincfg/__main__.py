
import argparse

from . import mincfg


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("bnf", type=argparse.FileType('r'),
                        help="path to BNF grammar file")
    parser.add_argument("expr", type=str,
                        help="string to check whether it's accepted by the grammar, or a path to a file")
    parser.add_argument("-f", "--file", action="store_true",
                        help="the expression is intepreted as a file path")
    parser.add_argument("-l", "--long", action="store_true",
                        help="preserve the long terminals")
    parser.add_argument("-c", "--compile-cnf", action="store_true",
                        help="parse the bnf and compile to normal form")
    args = parser.parse_args()

    bnf = args.bnf.read()

    if args.compile_cnf:
        if args.long:
            raise Exception("cannot compile preserving long terminals")
        cfl = mincfg.CFLRecognizer(bnf, False)
        with open(args.expr, 'w') as fd:
            for a, (b, c) in cfl.grammar_cnf:
                a = -(a + 1)
                if isinstance(b, int):
                    b = -(b + 1)
                else:
                    b = ord(b)
                if isinstance(c, int):
                    c = -(c + 1)
                else:
                    c = ord(c)
                fd.write(f"{a} {b} {c}\n")
        return

    string = args.expr
    if args.file:
        with open(string) as fp:
            string = fp.read()

    if mincfg.match(bnf, string, args.long):
        print("Yes")
    else:
        print("No")


if __name__ == "__main__":
    main()
