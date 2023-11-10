import sys
import os
from enum import Enum
from parser.ll1_utils import *
from scanner.scanner import Scanner
from parser.parser import Parser

class TokenType(Enum):
    NONE = 0
    BREAK = 1
    SPACE = 2
    NOT_TERMINAL = 3
    ARROW = 4
    DELIMITER = 5
    TERMINAL = 6

# should be in priority sort (ex. breakline before space)
token_regex = {    
    TokenType.BREAK: r'^\n',
    TokenType.SPACE: r'^\s',
    TokenType.NOT_TERMINAL: r'^<([a-zA-Z][a-zA-Z0-9_]*)>',
    TokenType.ARROW: r'^(->)',
    TokenType.DELIMITER: r'^[\|]',
    TokenType.TERMINAL: r'^(([a-zA-Z][a-zA-Z0-9_]*)|.)'
}

class GramGenerator:

    def __init__(self, parser: Parser):
        self.parser = parser

    def save(self, file_name: str):
        text = 'from enum import Enum\n'
        text += 'from parser.ll1_utils import *\n'
        text += 'from scanner.scanner import Scanner\n'
        text += 'from parser.parser import Parser, Node\n\n'
        text += 'class TokenType(Enum):\n'
        text += '    NONE = 0\n'
        text += '    BREAK = 1\n'
        text += '    SPACE = 2\n'
        text += '    ID = 3\n\n'
        text += '# should be in priority sort (ex. breakline before space)\n'
        text += 'token_regex = {    \n'
        text += "    TokenType.BREAK: r'^\\n',\n"
        text += "    TokenType.SPACE: r'^\\s',\n"
        text += "    TokenType.ID: r'^(([a-zA-Z][a-zA-Z0-9_]*)|.)'\n"
        text += "}\n\n"
        text += "class CodeGenerator:\n\n"
        text += "    def __init__(self, parser: Parser):\n"
        text += "        self.parser = parser\n\n"
        text += "    def generate(self):\n"
        text += "        self.parser.print_nodes()\n\n"
        text += f'{self.content}\n\n'
        text += "def syntactic_table_generate(gram: dict):\n"
        text += "    nterms = get_nterms(gram)\n"
        text += "    terms = get_terms(gram)\n"
        text += "    firsts = get_firsts(gram, nterms)\n"
        text += "    follows = get_follows(gram, nterms, firsts)\n"
        text += "    table = get_table(gram, nterms, terms, firsts, follows)\n"
        text += "    text = 'table: list = [\\n'\n"
        text += "    for i, row in enumerate(table):\n"
        text += "        text += '\\t['\n"
        text += "        for e, col in enumerate(row):\n"
        text += "            if isinstance(col, str):\n"
        text += "                text += f\"'{col}'\"\n"
        text += "            else:\n"
        text += "                text += f'{col}'\n"
        text += "            if e < len(row) -1:\n"
        text += "                text += ', '\n"
        text += "        text += ']'\n"
        text += "        if i < len(table) - 1:\n"
        text += "            text += ','\n"
        text += "        text += '\\n'\n"
        text += "    text += ']'\n"
        text += "    print(text)\n\n"
        text += 'if __name__ == "__main__":\n'
        text += '    # execute one time this code, after copy the code generated and reclace the method syntactic_table_generate with the content"\n'
        text += '    # to finish, remove this code and uncomment the others"\n'
        text += '    syntactic_table_generate(gram)\n'
        text += '    #source = input("source: ")\n'
        text += '    #scanner = Scanner(token_regex, TokenType.SPACE)\n'
        text += '    #tokens = scanner.scan(source)\n'
        text += '    #parser = Parser(table, TokenType.NONE)\n'
        text += '    #parser.parse(tokens)\n'
        text += '    #generator = CodeGenerator(parser)\n'
        text += '    #generator.generate()\n'
        with open(file_name, 'w') as arquivo:
            arquivo.write(text)

    def generate(self):
        self.content = 'gram: dict = {\n'
        tree = self.parser.get_tree()
        self.block_prod(tree.get_nodes('<BLOCK-PROD>'))
        self.content += '}'

    def block_prod(self, nodes: list):
        for i, blc in enumerate(reversed(nodes)):
            self.content += f'\t"{blc.get_child(2).token.value}": ['
            self.production(blc.get_nodes('<PRODUCTION>'))
            self.content += ']'
            if i < len(nodes) - 1:
                self.content += ','
            self.content += '\n'

    def production(self, nodes: list):
        for i, prd in enumerate(reversed(nodes)):
            self.content += '['
            self.term(prd.get_nodes('<TERM>'))
            self.content += ']'
            if i < len(nodes) - 1:
                self.content += ', '

    def term(self, nodes: list):
        for i, term in enumerate(reversed(nodes)):
            self.content += f'"{term.get_child(0).token.value}"'
            if i < len(nodes) - 1:
                self.content += ', '
    
gram: dict = {    
    "<TABLE>": [["<BLOCK-PROD>", "<TABLE-2>"]],
    "<TABLE-2>": [["BREAK", "<BLOCK-PROD>", "<TABLE-2>"],["ε"]],
    "<BLOCK-PROD>": [["NOT_TERMINAL", "ARROW", "<LIST-PROD>"]],

    "<LIST-PROD>": [["<PRODUCTION>", "<LIST-PROD-2>"]],
    "<LIST-PROD-2>": [["DELIMITER", "<PRODUCTION>", "<LIST-PROD-2>"],["ε"]],

    "<PRODUCTION>": [["<TERM>", "<PRODUCTION-2>"]],
    "<PRODUCTION-2>": [["<TERM>", "<PRODUCTION-2>"],["ε"]],    
    "<TERM>": [["NOT_TERMINAL"], ["TERMINAL"]]
}

def syntactic_table_generate(gram: dict):
    nterms = get_nterms(gram)
    terms = get_terms(gram)
    firsts = get_firsts(gram, nterms) 
    follows = get_follows(gram, nterms, firsts)
    table = get_table(gram, nterms, terms, firsts, follows)

    #print(f'nterm: {nterms}')
    #print(f'term: {terms}')
    #print(f'firsts: {firsts}')
    #print(f'follows: {follows}\n')
    
    #print('SYNTACTIC ANALYSIS TABLE')
    #print_table(table)

    return table

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print('Provide the LL(1) grammar file')
        exit(0)

    #gram_file = 'examples/expression.txt'
    #gram_file = 'examples/list.txt'
    gram_file = sys.argv[1]

    gram_text = ''
    with open(gram_file, 'r') as file:
        gram_text = file.read()

    table = syntactic_table_generate(gram)

    scanner = Scanner(token_regex, TokenType.SPACE)
    tokens = scanner.scan(gram_text)

    parser = Parser(table, TokenType.NONE)
    parser.parse(tokens)
    #parser.print_nodes(False)

    generator = GramGenerator(parser)
    generator.generate()

    file_name = f'{os.path.basename(gram_file)}'
    file_name = os.path.splitext(file_name)[0]
    file_name = f'{file_name}_main.py'
    generator.save(file_name)

    print(f'File {file_name} created with success!')