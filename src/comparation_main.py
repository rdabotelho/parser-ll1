from enum import Enum
from parser.ll1_utils import *
from scanner.scanner import Scanner
from parser.parser import Parser, Node

class TokenType(Enum):
    NONE = 0
    OPERATOR = 1,
    NUM = 2
    SPACE = 3

# should be in priority sort (ex. breakline before space)
token_regex = {    
    TokenType.OPERATOR: r'^(==|!=|<=|>=|<|>)',
    TokenType.NUM: r'^\d+',
    TokenType.SPACE: r'^\s',
} 

class CodeGenerator:

    def __init__(self, parser: Parser):
        self.parser = parser

    def generate(self):
        tree = self.parser.get_tree()
        result = self.expr(tree.get_node('<expr>'))
        print(result)

    def expr(self, node: Node) -> bool:
        term1 = self.term(node.get_child(2))
        oper = node.get_child(1).token.value
        term2 = self.term(node.get_child(0))
        if oper == '>':
            return term1 > term2
        elif oper == '<':
            return term1 < term2
        elif oper == '>=':
            return term1 <= term2
        elif oper == '<=':
            return term1 >= term2
        elif oper == '==':
            return term1 >= term2
        else:
            return term1 >= term2

    def term(self, node: Node) -> int:
        return self.num_value(node.get_child(0).token.value)
    
    def num_value(self, value: str) -> int:
        return int(value)

gram: dict = {
	"<expr>": [["<term>", "OPERATOR", "<term>"]],
	"<term>": [["NUM"]]
}

table: list = [
    ['', 'OPERATOR', 'NUM', '$'],
    ['<expr>', [], ['<term>', 'OPERATOR', '<term>'], []],
    ['<term>', [], ['NUM'], []]
]

if __name__ == "__main__":
    print((3 > 2 > 1) > 1)
    source = input("source: ")
    scanner = Scanner(token_regex, TokenType.SPACE)
    tokens = scanner.scan(source)
    parser = Parser(table, TokenType.NONE)
    parser.parse(tokens)
    generator = CodeGenerator(parser)
    generator.generate()
