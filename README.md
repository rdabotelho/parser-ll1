# Parser Generator

This generator has the objective to facilitate the creation of an LL(1) parser, from a context-free grammar txt file of type LL(1), the generator will create the set of firsts, set of follows and the LL(1) syntactic analysis table.
In addition to generating these artifacts, we also provide the scanner algorithm for lexical analysis and the LL(1) parser algorithm for top-down syntactic analysis.
We also provide some example files with LL(1) context-free grammars in the examples folder:

- arithmetic.txt: Example grammar for arithmetic expression
- comparation.txt: Example grammar for comparation expression
- list.txt: Example grammar for a comma separated list

See a step-by-step guide on how to generate it

Let's to create a parser of logical expression

1. Create the txt file with the context-free grammar LL(1) (cannot be ambiguous and have left recursion).

_examples/logical.txt_
```
<expr>   -> <term> <expr2>
<expr2>  -> OR <term> <expr2> | ε
<term>   -> <factor> <term2>
<term2>  -> AND <factor> <term2> | ε
<factor> -> NOT <factor> | BOOL |  ( <expr> )
```

2. Execute the main.py passing the file name as argument to the generation.

```
python3 main.py examples/logical.txt
```

The result will be the file `logical_main.py`

3. Now, execute the file `logical_main.py` to generate the code of the syntactic table.

```
python3 logical_main.py
```

4. Copy the generated code of the syntactic table and paste replacing the method `syntactic_table_generate` in the file `logical_main.py`.

_syntactic table generated_
```python
table: list = [
    ['', 'OR', 'AND', 'NOT', 'BOOL', '(', ')', '$'],
    ['<expr>', [], [], ['<term>', '<expr2>'], ['<term>', '<expr2>'], ['<term>', '<expr2>'], [], []],
    ['<expr2>', ['OR', '<term>', '<expr2>'], [], [], [], [], ['ε'], ['ε']],
    ['<term>', [], [], ['<factor>', '<term2>'], ['<factor>', '<term2>'], ['<factor>', '<term2>'], [], []],
    ['<term2>', ['ε'], ['AND', '<factor>', '<term2>'], [], [], [], ['ε'], ['ε']],
    ['<factor>', [], [], ['NOT', '<factor>'], ['BOOL'], ['(', '<expr>', ')'], [], []]
]
```

5. Comment the code `syntactic_table_generate(gram)` in main method and uncomment others lines, as information in the comments 

6. Define the token types of grammatical to the lexical analyzer.

```python
class TokenType(Enum):
    NONE = 0
    NOT = 1,
    AND = 2,
    OR = 3,
    BOOL = 4
    DELIMITER = 5
    ID = 6
    SPACE = 7

# should be in priority sort (ex. breakline before space)
token_regex = {    
    TokenType.NOT: r'^\b(?:not)\b',
    TokenType.AND: r'^\b(?:and)\b',
    TokenType.OR: r'^\b(?:or)\b',
    TokenType.BOOL: r'^\b(?:true|false)\b',
    TokenType.DELIMITER: r'^[\(\)]',
    TokenType.ID: r'^[a-zA-Z][a-zA-Z0-9_]*',
    TokenType.SPACE: r'^\s',
}    
```

7. Finally, just implement, in the CodeGenerator class, the generation methods based on the LL(1) grammar that will interpret the logical expression input, according to the following code:

```python
class CodeGenerator:

    def __init__(self, parser: Parser):
        self.parser = parser

    def generate(self):
        tree = self.parser.get_tree()
        result = self.expr(tree.get_node('<expr>'))
        print(result)

    def expr(self, node: Node) -> bool:
        term = self.term(node.get_child(1))
        return self.expr2(term, node.get_child(0))

    def expr2(self, term1: bool, node: Node) -> bool:  
        if len(node.children) > 1:  
            term2 = self.term(node.get_child(1))
            term3 = term1 or term2
            return self.expr2(term3, node.get_child(0)) 
        return term1
    
    def term(self, node: Node) -> bool:
        factor = self.factor(node.get_child(1))
        return self.term2(factor, node.get_child(0))
    
    def term2(self, factor1: bool, node: Node) -> bool:
        if len(node.children) > 1:  
            factor2 = self.factor(node.get_child(1))
            factor3 = factor1 and factor2
            return self.term2(factor3, node.get_child(0))                
        return factor1

    def factor(self, node: Node) -> bool:
        if len(node.children) > 1:
            if node.get_child(0).value == ')':
                expr = node.get_child(1)
                return self.expr(expr)
            else:
                return not self.factor(node.get_child(0))
        else:
            return self.bool_value(node.get_child(0).token.value)
    
    def bool_value(self, value: str) -> bool:
        return value == 'true'
```

8. Now, test the interpreter passing the logical expression.

```
python3 logical_main.py
```

```
Logical expression: true and (true or false)
```
