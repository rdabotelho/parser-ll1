import re
from mytoken import TokenType, Token, token_regex
from mynode import Node
from myresolver import *
from commons.exceptions import *

class Parser:

    def __init__(self, object: any, printSyntree: bool = False):
        self.object = object
        self.printSyntree = printSyntree
        self.prod = 0

    def execute(self, source: str) -> any:
        self.lex(source)
        self.syn()
        self.sem()
        self.interpret()
        return None
    
    def interpret(self) -> any:
        self.not_terms = []
        self.terms = []
        for nt in self.syntree.children:
            self.not_terms.append(nt)
        self.extract_terms(self.syntree)

        str = "parsing_table = {\n"
        for not_term in self.syntree.children:
            for prod in not_term.children:       
                str2 = '' 
                term = None
                for it in prod.children:
                    str2 += f"{it.token.value}"        
                    if it.token.type == TokenType.TERM:
                        term = it
                if term != None:
                    str += f"\t('{not_term.token.value}', '{term.token.value}'): '{str2}',\n"
        str += "}\n"

        print(str)

    def extract_terms(self, node: Node = None) -> any:
        if node.token.type == TokenType.TERM:
            exist = False
            for it in self.terms:
                if it.token.value == node.token.value:
                    exist = True
                    break
            if exist == False:
                self.terms.append(node)
        for child in node.children:
            self.extract_terms(child)

    def read_token(self, sequence: str):
        sub_sequence = sequence[self.pos:]
        for type in TokenType:
            if type == TokenType.NONE:
                continue
            match = re.search(token_regex[type], sub_sequence)
            if match:
                value = match.group()
                token = Token(type, value, self.pos + 1)
                self.pos += len(value)
                return token
        if len(sub_sequence) > 0:
            raise LexicalException(f'Unidentified token in position {self.pos}')
        return None
    
    def lex(self, sequence: str):
        self.tokens = []
        self.pos = 0
        while True:
            token = self.read_token(sequence) 
            if token:
                if token.type != TokenType.SPACE:
                    self.tokens.append(token)
            else:
                break
        #self.print_lex()   
    
    def syn(self):
        self.pos = 0
        self.syntree = self.create_node(Token(TokenType.NONE, '$', 0))
        if not ((len(self.tokens) == 0 or self.table(self.syntree)) and self.is_end()):
            token = self.next_token()
            raise SyntacticException(f'Token not expected \"{token.value}\" in position {token.pos}')
        if self.printSyntree:
            self.print_syn()
        
    def sem(self):
        if len(self.tokens) > 0:
            return self.syntree.eval(self.object)
        return None

    '''
    TABLE       -> <BLOCK-PROD> break <TABLE> || <BLOCK-PROD>
    BLOCK-PROD  -> <ID> -> <LIST-PROD>
    LIST-PROD   -> <PRODUCTION> | <LIST-PROD> || <PRODUCTION>
    PRODUCTION  -> TERM <PRODUCTION> || TERM
    TERM        -> ID || OTHER   
    '''

    def table(self, parent: Node) -> bool:
        start = self.pos
        node_left = self.create_node(Token(TokenType.NONE, 'PROD ', start))
        node_right = self.create_node(Token(TokenType.NONE, 'RIGHT', start))
        result = (
            ((self.block_prod(node_left) and self.terminator(TokenType.BREAK) and self.table(node_right) and self.end(1)) or self.reset(start)) or
            ((self.block_prod(node_left) and self.end(2)) or self.reset(start))
        )
        if result:
            parent.copy(node_left)
            if self.prod == 1:
                for node in node_right.children:
                    parent.add_child(node)
        return result
    
    def block_prod(self, parent: Node) -> bool:     
        start = self.pos
        node_left = self.create_node(Token(TokenType.NONE, 'LEFT', start))
        node_right = self.create_node(Token(TokenType.NONE, 'RIGHT', start))
        result = (
            ((self.terminator(TokenType.NOT_TERM, None, node_left) and self.terminator(TokenType.ARROW) and self.list_prod(node_right)) or self.reset(start))
        )
        if result:
            parent.clear_children() 
            for node in node_right.children:
                node_left.add_child(node)
            parent.add_child(node_left)
        return result
    
    def list_prod(self, parent: Node) -> bool:        
        start = self.pos
        node_left = self.create_node(Token(TokenType.NONE, 'PROD', start))
        node_right = self.create_node(Token(TokenType.NONE, 'PROD', start))
        result = (
            ((self.production(node_left) and self.terminator(TokenType.DELIMITER) and self.list_prod(node_right) and self.end(1)) or self.reset(start)) or
            ((self.production(node_left) and self.end(2)) or self.reset(start))
        )
        if result:
            parent.clear_children() 
            parent.add_child(node_left)
            if self.prod == 1:
                for node in node_right.children:
                    parent.add_child(node)
        return result
    
    def production(self, parent: Node) -> bool:        
        start = self.pos
        node_left = self.create_node(Token(TokenType.NONE, 'LEFT', start))
        node_right = self.create_node(Token(TokenType.NONE, 'RIGHT', start))
        result = (
            ((self.term(node_left) and self.production(node_right) and self.end(1)) or self.reset(start)) or
            ((self.term(node_left) and self.end(2)) or self.reset(start))
        )
        if result:           
            parent.clear_children() 
            parent.add_child(node_left)
            if self.prod == 1:
                for node in node_right.children:
                    parent.add_child(node)
        return result
    
    def term(self, parent: Node) -> bool:        
        start = self.pos
        node_left = self.create_node(Token(TokenType.NONE, 'LEFT', start))
        result = (
            ((self.terminator(TokenType.NOT_TERM, None, node_left) and self.end(1)) or self.reset(start)) or
            ((self.terminator(TokenType.TERM, None, node_left) and self.end(2)) or self.reset(start))
        )
        if result:
            parent.copy(node_left)
        return result
    
    # Utils methods

    def terminator(self, type: TokenType, value: str = None, node: Node = None) -> bool:
        token = self.next_token()
        if node != None:
            node.token = token
        return (token != None) and (token.type == type) and ((value == None) or (value == token.value))

    def next_token(self) -> Token:
        token = None
        size = len(self.tokens)
        if (size > 0) and (self.pos < size):
            token = self.tokens[self.pos]
            self.pos += 1
        return token

    def reset(self, start: int, node: Node = None) -> bool:
        self.pos = start
        if node != None:
            node.clear_children()
        return False

    def end(self, prod: int) -> bool:
        self.prod = prod
        return True

    def is_end(self) -> bool:
        return self.pos == len(self.tokens)
    
    def cover(self, node: Node, value: any) -> bool:
        child = self.create_node(Token(TokenType.NOT_TERM, value, 0))
        node.add_child(child)
        return child
    
    def set_resolver(self, node: Node, resolver: Resolver) -> bool:
        if node.token.type == TokenType.NONE:
            node = node.last_child()
        if node.resolver == None:
            node.resolver = resolver
        return True
    
    def create_node(self, token: Token, resolver: Resolver = None) -> Node:
        node = Node(token)
        node.session = self.object
        node.resolver = resolver
        return node

    def print_lex(self):
        print('### lexical analysis ###')
        for token in self.tokens:
            print(token)
        print('')

    def print_syn(self, node: Node = None, level: int = 0) -> bool:
        if len(self.tokens) == 0:
            return   
        if node == None:
            node = self.syntree
            print('### syntax analisys ###')
        else:
            print("  " * level + str(node))
        for child in node.children:
            self.print_syn(child, level + 1)
        return True
