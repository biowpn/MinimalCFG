
import argparse

from . import mincfg


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("cfg", type=argparse.FileType('r'),
                        help="path to a file that specifies a CFG")
    parser.add_argument("input", type=str,
                        help="path to a file whose content is to check whether being accepted by the grammar")
    parser.add_argument("-s", "--string", action="store_true",
                        help="interpret the second positional argument as direct input string rather than a file path")
    parser.add_argument("-l", "--long", action="store_true",
                        help="preserve the long terminals")
    parser.add_argument("-c", "--compile-cnf", action="store_true",
                        help="compile the grammar to normal form, second positional arg being the output file path")
    args = parser.parse_args()

    cfg = args.cfg.read()

    if args.compile_cnf:
        if args.long:
            raise Exception("cannot compile when preserving long terminals")
        cfl = mincfg.CFLRecognizer(cfg, False)
        with open(args.input, 'w') as fd:
            for a, (b, c) in cfl.grammar_cnf:
                if isinstance(b, str):
                    b = ord(b)
                if isinstance(c, str):
                    c = ord(c)
                fd.write(f"{a} {b} {c}\n")
        return

    if args.string:
        string = args.input
    else:
        with open(string) as fp:
            string = fp.read()

    if mincfg.match(cfg, string, args.long):
        print("Yes")
    else:
        print("No")


if __name__ == "__main__":
    main()
