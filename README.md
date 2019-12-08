# Minimal Context-Free Grammar Engine

Python implementation of a minimal CFG engine, which can build arbitrary CFL recognizer given CFG.

See also: [Minimal Regular Expression Engine](https://github.com/ymenghank/MinimalRegEx)

## Usage

- Python

    1. directly calling `match`:
        ```
        import CFG

        CFG.match(r"S:{S}{S};S:();S:;", "(())()")
        ```

    2. construct a CFL recognizer first and call `match` later:

        ```
        import CFG

        r = CFG.compile(r"S:{S}{S};S:();S:;")
        r.match("(())()")
        ```

## Testing

- Python
    - run [test.py](./python/test.py)

## Credits

Essentially CYK algorithm. Other algorithms by *[Elements of the Theory of Computation](https://dl.acm.org/citation.cfm?id=549820)* (2nd Edition) by Harry R. Lewis and Christos H. Papadimitriou.
