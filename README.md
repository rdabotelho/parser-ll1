# Parser Generator

This generator has the objective to facilitate the creation of an LL(1) parser, from a context-free grammar txt file of type LL(1), the generator will create the set of firsts, set of follows and the LL(1) syntactic analysis table.
In addition to generating these artifacts, we also provide the scanner algorithm for lexical analysis and the LL(1) parser algorithm for top-down syntactic analysis.
We also provide some example files with LL(1) context-free grammars in the examples folder:

- expression.txt: Example grammar for arithmetic expression
- list.txt: Example grammar for a comma separated list

See a step-by-step guide on how to generate it

Let's to create a parser of logical operation

1. Create the txt file with the context-free grammar LL(1) (cannot be ambiguous and have left recursion)

_examples/logical.txt_
```
<expr>   -> <term> <expr2>
<expr2>  -> or <term> <expr2> | ε
<term>   -> <factor> <term2>
<term2>  -> and <factor> <term2> | ε
<factor> -> not <factor> | id | true | false | ( <expr> )
```

2. Execute the main.py to generate

```
python3 main.py examples/logical.txt
```

The generate shows as information:
- Not terminals Set
- Terminals Set
- Firsts Set
- Follows Set
- Syntactic Analysis Table
- Syntactic Analysis Tree

