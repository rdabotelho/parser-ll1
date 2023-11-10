from enum import Enum
from parser.ll1_utils import *
from scanner.scanner import Scanner
from parser.parser import Parser, Node

class TokenType(Enum):
    NONE = 0,
    BOOL = 1
    OPERATOR_LOGIC = 2
    ID = 3
    DELIMITER = 4
    OPERATOR_COMP = 5
    OPERATOR_ARITH = 6
    DECIMAL = 7
    INTEGER = 8
    STRING = 9
    SPACE = 10

token_regex = {
    TokenType.BOOL: r'^\b(?:true|false)\b',
    TokenType.OPERATOR_LOGIC: r'^\b(?:and|or|not)\b',
    TokenType.ID: r'^[a-zA-Z][a-zA-Z0-9_]*',
    TokenType.DELIMITER: r'^[\(\)\,\.]',
    TokenType.OPERATOR_COMP: r'^(==|!=|<=|>=|<|>)',
    TokenType.OPERATOR_ARITH: r'^[\+\-\*\/]',
    TokenType.DECIMAL: r'^\d+(\.\d+)',
    TokenType.INTEGER: r'^\d+',
    TokenType.STRING: r'^\'(.*?)\'',
    TokenType.SPACE: r'^\s'
}

class PropFunc:

    def __init__(self, name: str, params: list = None):
        self.name = name
        self.params = params
        self.value = None

    def is_property(self) -> bool:
        return self.params == None

    def is_function(self) -> bool:
        return not self.is_property() 

    def calc(self, next: any = None) -> any:
        return None

class CodeGenerator:

    def __init__(self, parser: Parser):
        self.parser = parser

    def generate(self):
        tree = self.parser.get_tree()
        result = self.expr(tree.get_node('<expr>'))
        print(result)

    def expr(self, node: Node) -> int:
        return self.expr_logic(node.get_child(0))

    def expr_logic(self, node: Node) -> any:
        prior = self.term_logic(node.get_child(1))
        return self.expr_logic2(prior, node.get_child(0))
    
    def expr_logic2(self, prior: any, node: Node) -> any:
        if len(node.children) > 1:  
            next = self.term_logic(node.get_child(1))
            result = prior or next
            return self.expr_logic2(result, node.get_child(0))                
        return prior
    
    def term_logic(self, node: Node) -> any:
        prior = self.factor_logic(node.get_child(1))
        return self.term_logic2(prior, node.get_child(0))

    def term_logic2(self, prior: any, node: Node) -> any:
        if len(node.children) > 1:  
            next = self.factor_logic(node.get_child(1))
            result = prior and next
            return self.term_logic2(result, node.get_child(0))                
        return prior

    def factor_logic(self, node: Node) -> any:
        if len(node.children) > 1:  
            next = self.factor_logic(node.get_child(1))
            result = not next
            return self.expr_comp(result, node.get_child(0))                
        return self.expr_comp(node.get_child(0))

    def expr_comp(self, node: Node) -> bool:
        prior = self.expr_arith(node.get_child(1))
        return self.expr_comp2(prior, node.get_child(0))
    
    def expr_comp2(self, prior: bool, node: Node) -> bool:
        if len(node.children) > 1:  
            oper = node.get_child(2).token.value
            next = self.expr_arith(node.get_child(1))
            result = None
            if oper == '==':
                result = prior == next
            elif oper == '!=':
                result = prior != next
            elif oper == '<=':
                result = prior <= next
            elif oper == '>=':
                result = prior >= next
            elif oper == '<':
                result = prior < next
            else:
                result = prior > next
            return self.expr_comp2(result, node.get_child(0))                
        return prior    

    def expr_arith(self, node: Node) -> any:
        term = self.term_arith(node.get_child(1))
        return self.expr_arith2(term, node.get_child(0))
    
    def expr_arith2(self, prior: any, node: Node) -> any:
        if len(node.children) > 1:  
            oper = node.get_child(2).token.value
            next = self.term_arith(node.get_child(1))
            result = None
            if oper == '+':
                result = prior + next
            else:
                result = prior - next
            return self.expr_arith2(result, node.get_child(0))                
        return prior

    def term_arith(self, node: Node) -> any:
        term = self.term(node.get_child(1))
        return self.term_arith2(term, node.get_child(0))
    
    def term_arith2(self, prior: any, node: Node) -> any:
        if len(node.children) > 1:  
            oper = node.get_child(2).token.value
            next = self.term(node.get_child(1))
            result = None
            if oper == '*':
                result = prior * next
            else:
                result = prior / next
            return self.term_arith2(result, node.get_child(0))                
        return prior

    def term(self, node: Node) -> any:
        if len(node.children) > 1:
            return self.expr(node.get_child(1))
        else:
            tp = node.get_child(0)
            if tp.value == '<literal>':
                return self.literal(tp)
            else:
                return self.variable(tp)

    def variable(self, node: Node) -> any:
        prior = self.identifier(node.get_child(1))
        next = self.variable2(prior, node.get_child(0))
        if next == None:
            return prior.calc()
        return next.calc(prior)
    
    def variable2(self, prior: PropFunc, node: Node) -> PropFunc:
        if len(node.children) > 1:
            next = self.identifier(node.get_child(1))
            next.calc(prior)
            return self.variable2(next, node.get_child(0))
        return prior

    def identifier(self, node: Node) -> PropFunc:
        name = self.prop_func(node.get_child(1))
        params = self.parameters(node.get_child(0))
        if params == None:
            return PropFunc(name)
        else:
            return PropFunc(name, params)
    
    def identifier2(self, node: Node) -> any:
        if len(node.children) > 1:
            return self.parameters(node.get_child(1))
        return None

    def parameters(self, node: Node) -> list:
        params = []
        param = self.expr(node.get_child(1))
        params.append(param)
        self.parameters2(params, node.get_child(0))
        return params
    
    def parameters2(self, params: list, node: Node) -> None:
        if len(node.children) > 1:
            param = self.expr(node.get_child(1))
            params.append(param)
            return self.parameters2(params, node.get_child(0))
        return None       

    def prop_func(self, node: Node) -> str:
        return node.get_child(0).token_value

    def literal(self, node: Node) -> any:
        tp = node.get_child(0)
        name = tp.token.type.name
        value = tp.token.value
        if name == 'DECIMAL':
            return self.decimal(value)
        elif name == 'INTEGER':
            return self.integer(value)
        elif name == 'STRING':
            return self.string(value)
        else:
            return self.bool(value)
    
    def decimal(self, value: str) -> any:
        return float(value)
    
    def integer(self, value: str) -> any:
        return int(value)

    def string(self, value: str) -> any:
        return value.replace("'", "")
    
    def bool(self, value: str) -> any:
        return value == 'true'

table: list = [
    ['', 'or', 'and', 'not', 'OPERATOR_COMP', '+', '-', '*', '/', '(', ')', '.', ',', 'ID', 'DECIMAL', 'INTEGER', 'STRING', 'BOOL', '$'],
    ['<expr>', [], [], ['<expr_logic>'], [], [], [], [], [], ['<expr_logic>'], [], [], [], ['<expr_logic>'], ['<expr_logic>'], ['<expr_logic>'], ['<expr_logic>'], ['<expr_logic>'], []],
    ['<expr_logic>', [], [], ['<term_logic>', '<expr_logic2>'], [], [], [], [], [], ['<term_logic>', '<expr_logic2>'], [], [], [], ['<term_logic>', '<expr_logic2>'], ['<term_logic>', '<expr_logic2>'], ['<term_logic>', '<expr_logic2>'], ['<term_logic>', '<expr_logic2>'], ['<term_logic>', '<expr_logic2>'], []],
    ['<expr_logic2>', ['or', '<term_logic>', '<expr_logic2>'], [], [], [], [], [], [], [], [], ['ε'], [], ['ε'], [], [], [], [], [], ['ε']],
    ['<term_logic>', [], [], ['<factor_logic>', '<term_logic2>'], [], [], [], [], [], ['<factor_logic>', '<term_logic2>'], [], [], [], ['<factor_logic>', '<term_logic2>'], ['<factor_logic>', '<term_logic2>'], ['<factor_logic>', '<term_logic2>'], ['<factor_logic>', '<term_logic2>'], ['<factor_logic>', '<term_logic2>'], []],
    ['<term_logic2>', ['ε'], ['and', '<factor_logic>', '<term_logic2>'], [], [], [], [], [], [], [], ['ε'], [], ['ε'], [], [], [], [], [], ['ε']],
    ['<factor_logic>', [], [], ['not', '<factor_logic>'], [], [], [], [], [], ['<expr_comp>'], [], [], [], ['<expr_comp>'], ['<expr_comp>'], ['<expr_comp>'], ['<expr_comp>'], ['<expr_comp>'], []],
    ['<expr_comp>', [], [], [], [], [], [], [], [], ['<expr_arith>', '<expr_comp2>'], [], [], [], ['<expr_arith>', '<expr_comp2>'], ['<expr_arith>', '<expr_comp2>'], ['<expr_arith>', '<expr_comp2>'], ['<expr_arith>', '<expr_comp2>'], ['<expr_arith>', '<expr_comp2>'], []],
    ['<expr_comp2>', ['ε'], ['ε'], [], ['OPERATOR_COMP', '<expr_arith>', '<expr_comp2>'], [], [], [], [], [], ['ε'], [], ['ε'], [], [], [], [], [], ['ε']],
    ['<expr_arith>', [], [], [], [], [], [], [], [], ['<term_arith>', '<expr_arith2>'], [], [], [], ['<term_arith>', '<expr_arith2>'], ['<term_arith>', '<expr_arith2>'], ['<term_arith>', '<expr_arith2>'], ['<term_arith>', '<expr_arith2>'], ['<term_arith>', '<expr_arith2>'], []],
    ['<expr_arith2>', ['ε'], ['ε'], [], ['ε'], ['+', '<term_arith>', '<expr_arith2>'], ['-', '<term_arith>', '<expr_arith2>'], [], [], [], ['ε'], [], ['ε'], [], [], [], [], [], ['ε']],
    ['<term_arith>', [], [], [], [], [], [], [], [], ['<term>', '<term_arith2>'], [], [], [], ['<term>', '<term_arith2>'], ['<term>', '<term_arith2>'], ['<term>', '<term_arith2>'], ['<term>', '<term_arith2>'], ['<term>', '<term_arith2>'], []],
    ['<term_arith2>', ['ε'], ['ε'], [], ['ε'], ['ε'], ['ε'], ['*', '<term>', '<term_arith2>'], ['/', '<term>', '<term_arith2>'], [], ['ε'], [], ['ε'], [], [], [], [], [], ['ε']],
    ['<term>', [], [], [], [], [], [], [], [], ['(', '<expr>', ')'], [], [], [], ['<variable>'], ['<literal>'], ['<literal>'], ['<literal>'], ['<literal>'], []],
    ['<variable>', [], [], [], [], [], [], [], [], [], [], [], [], ['<identifier>', '<variable2>'], [], [], [], [], []],
    ['<variable2>', ['ε'], ['ε'], [], ['ε'], ['ε'], ['ε'], ['ε'], ['ε'], [], ['ε'], ['.', '<identifier>', '<variable2>'], ['ε'], [], [], [], [], [], ['ε']],
    ['<identifier>', [], [], [], [], [], [], [], [], [], [], [], [], ['<prop_func>', '<identifier2>'], [], [], [], [], []],
    ['<identifier2>', ['ε'], ['ε'], [], ['ε'], ['ε'], ['ε'], ['ε'], ['ε'], ['(', '<parameters>', ')'], ['ε'], ['ε'], ['ε'], [], [], [], [], [], ['ε']],
    ['<parameters>', [], [], ['<expr>', '<parameters2>'], [], [], [], [], [], ['<expr>', '<parameters2>'], [], [], [], ['<expr>', '<parameters2>'], ['<expr>', '<parameters2>'], ['<expr>', '<parameters2>'], ['<expr>', '<parameters2>'], ['<expr>', '<parameters2>'], []],
    ['<parameters2>', [], [], [], [], [], [], [], [], [], ['ε'], [], [',', '<expr>', '<parameters2>'], [], [], [], [], [], []],
    ['<prop_func>', [], [], [], [], [], [], [], [], [], [], [], [], ['ID'], [], [], [], [], []],
    ['<literal>', [], [], [], [], [], [], [], [], [], [], [], [], [], ['DECIMAL'], ['INTEGER'], ['STRING'], ['BOOL'], []]
]

if __name__ == "__main__":
    source = input("source: ")
    scanner = Scanner(token_regex, TokenType.SPACE)
    tokens = scanner.scan(source)
    parser = Parser(table, TokenType.NONE)
    parser.parse(tokens)
    generator = CodeGenerator(parser)
    generator.generate()
