from parser.stack import Stack
from parser.node import Node
from parser.ll1_utils import is_term
from scanner.token import Token
from commons.exceptions import SyntacticException

# Parser LL(1)
class Parser:

    def __init__(self, table: list, none_type: any):
        self.table = table
        self.none_type = none_type

    def parse(self, tokens: list) -> Node:
        token_start = Token(self.none_type, '$', 0)
        node_start = Node('$')
        prod_start = self.table[1][0]
        self.stack = Stack(node_start)
        self.stack.push(Node(prod_start, node_start))
        self.pos = 0
        words = list(tokens)
        words.append(token_start)
        while True:
            # get the top of stack
            top: Node = self.stack.top()
            # get the word of lookahead
            lookahead: Token = words[self.pos]
            # check if is the end
            if top.value == '$' and lookahead == token_start:
                break
            # check if the terminal is igual the terminal of top
            if top.match(lookahead):
                top.token = lookahead
                self.stack.pop()
                self.pos += 1
            # if is not terminal, then find the produtions in the table
            else:
                #print(f'NO METCH: top: {top}, lookahead: {lookahead}')
                prod = self.find_in_table(top, lookahead)
                # if there is not production, then throw a syntactic error
                if len(prod) == 0:
                    raise SyntacticException(f'Token not expected \"{lookahead.value}\" in position {lookahead.pos}')
                # if there is production, then remove the not terminal of the stack   
                self.stack.pop()
                # if there is not ε in the production, then add production in the stack
                if prod[0] != 'ε':
                    for it in reversed(prod):
                        self.stack.push(Node(it, top))
        return self.stack.top()
    
    def get_tree(self) -> Node:
        return self.stack.top()

    def find_in_table(self, nterm: Node, term: Token) -> list:
        term_row = self.table[0]
        if term.type == self.none_type:
            value = '$'
        else:
            value = term.type.name
        col = term_row.index(value)
        if not (col > 0):
            return []
        for row in self.table:
            if row[0] == nterm.value:
                return row[col]
        return []
        
    def print_nodes(self, just_terminal: bool = False, node: Node = None, level: int = 0) -> bool:
        inc = 1
        if node == None:
            node = self.stack.top()
        elif just_terminal == False or node.is_terminal():
            print("  " * level + str(node))
        else:
             inc = 0
        for child in node.children:
            self.print_nodes(just_terminal, child, level + inc)
