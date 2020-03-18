
import argparse

from . import mincfg


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("bnf", type=argparse.FileType('r'),
                        help="path to BNF grammar file")
    parser.add_argument("expr", type=str,
                        help="string to check whether it's accepted by the grammar, or a path to a file whose content is to test")
    parser.add_argument("-f", "--file", action="store_true",
                        help="the expression is intepreted as a file path")
    parser.add_argument("-l", "--long", action="store_true",
                        help="preserve the long terminals")
    args = parser.parse_args()

    string = args.expr
    if args.file:
        with open(string) as fp:
            string = fp.read()

    bnf = args.bnf.read()
    if mincfg.match(bnf, string, args.long):
        print("Yes")
    else:
        print("No")


if __name__ == "__main__":
    main()
