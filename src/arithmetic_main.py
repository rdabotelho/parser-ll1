from enum import Enum
from parser.ll1_utils import *
from scanner.scanner import Scanner
from parser.parser import Parser, Node

class TokenType(Enum):
    NONE = 0
    OPERATOR = 1,
    DELIMITER = 2
    NUM = 3
    SPACE = 4

# should be in priority sort (ex. breakline before space)
token_regex = {    
    TokenType.OPERATOR: r'^[\+\-\*\/]',
    TokenType.DELIMITER: r'^[\(\)]',
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

    def expr(self, node: Node) -> int:
        term = self.term(node.get_child(1))
        return self.expr2(term, node.get_child(0))

    def expr2(self, term1: int, node: Node) -> int:  
        if len(node.children) > 1:
            oper = node.get_child(2).value
            term2 = self.term(node.get_child(1))
            term3 = term1
            if oper == '+':
                term3 += term2
            else:
                term3 -= term2
            return self.expr2(term3, node.get_child(0)) 
        return term1
    
    def term(self, node: Node) -> int:
        factor = self.factor(node.get_child(1))
        return self.term2(factor, node.get_child(0))
    
    def term2(self, factor1: int, node: Node) -> int:
        if len(node.children) > 1:  
            oper = node.get_child(2).value
            factor2 = self.factor(node.get_child(1))
            factor3 = factor1
            if oper == '*':
                factor3 *= factor2
            else:
                factor3 /= factor2
            return self.term2(factor3, node.get_child(0))                
        return factor1

    def factor(self, node: Node) -> int:
        if len(node.children) > 1:
            expr = node.get_child(1)
            return self.expr(expr)
        else:
            return self.num_value(node.get_child(0).token.value)
    
    def num_value(self, value: str) -> int:
        return int(value)

gram: dict = {
	"<expr>": [["<term>", "<expr2>"]],
	"<expr2>": [["+", "<term>", "<expr2>"], ["-", "<term>", "<expr2>"], ["ε"]],
	"<term>": [["<factor>", "<term2>"]],
	"<term2>": [["*", "<factor>", "<term2>"], ["/", "<factor>", "<term2>"], ["ε"]],
	"<factor>": [["NUM"], ["(", "<expr>", ")"]]
}

table: list = [
    ['', '+', '-', '*', '/', 'NUM', '(', ')', '$'],
    ['<expr>', [], [], [], [], ['<term>', '<expr2>'], ['<term>', '<expr2>'], [], []],
    ['<expr2>', ['+', '<term>', '<expr2>'], ['-', '<term>', '<expr2>'], [], [], [], [], ['ε'], ['ε']],
    ['<term>', [], [], [], [], ['<factor>', '<term2>'], ['<factor>', '<term2>'], [], []],
    ['<term2>', ['ε'], ['ε'], ['*', '<factor>', '<term2>'], ['/', '<factor>', '<term2>'], [], [], ['ε'], ['ε']],
    ['<factor>', [], [], [], [], ['NUM'], ['(', '<expr>', ')'], [], []]
]

if __name__ == "__main__":
    source = input("source: ")
    scanner = Scanner(token_regex, TokenType.SPACE)
    tokens = scanner.scan(source)
    parser = Parser(table, TokenType.NONE)
    parser.parse(tokens)
    generator = CodeGenerator(parser)
    generator.generate()
