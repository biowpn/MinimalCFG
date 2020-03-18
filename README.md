# Minimal Context-Free Grammar Engine

Build arbitrary Context-Free Language recognizer given its grammar in [BNF](https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form).

See also: [Minimal Regular Expression Engine](https://github.com/ymenghank/MinimalRegEx)

## Usage


Directly calling `match`:

```
mincfg.match(r"<S>::=<S><S> <S>::='('')' <S>::=''", "(())()")
```

Or, construct a CFL recognizer first and call `match` later:

```
r = mincfg.compile(r"<S>::=<S><S> <S>::='('')' <S>::=''", "(())()")
r.match("(())()")
```

## Command Line Usage

```
[In]  python -m mincfg .\examples\dna.bnf "ACCATCA"
[Out] Yes
```

```
[In]  python -m mincfg .\examples\dna.bnf "UGGUAGU"
[Out] No
```

```
[In]  python -m mincfg .\examples\arithmetic.bnf "(2 - 1)"
[Out] Yes
```

```
[In]  python -m mincfg .\examples\arithmetic.bnf "(2 (-) 1)"
[Out] No
```

```
[In]  python -m mincfg .\examples\arithmetic.bnf "(2 - -1)"
[Out] Yes
```

```
[In]  python -m mincfg .\examples\arithmetic.bnf "(2--1)"
[Out] Yes
```

```
[In]  python -m mincfg .\examples\arithmetic.bnf "(2-- 1)"
[Out] No
```

```
[In]  python -m mincfg .\examples\arithmetic.bnf "(2- -1)"
[Out] Yes
```

```
[In]  python -m mincfg .\examples\arithmetic.bnf "(2---1)"
[Out] Yes
```


## Testing

```
python -m mincfg.test
```

## Credits

Essentially CYK algorithm. Other algorithms by *[Elements of the Theory of Computation](https://dl.acm.org/citation.cfm?id=549820)* (2nd Edition) by Harry R. Lewis and Christos H. Papadimitriou.
