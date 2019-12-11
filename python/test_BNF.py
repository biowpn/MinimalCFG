
import parser_BNF

import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=argparse.FileType('r'),
                        help="file containing CFG in BNF")
    args = parser.parse_args()

    string = args.file.read()

    try:
        G = parser_BNF.parse(string)
    except parser_BNF.ParsingException as e:
        print(str(e))
        return

    for rule in G:
        print(rule)


if __name__ == "__main__":
    main()
