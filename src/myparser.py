import re
from mytoken import TokenType, Token, token_regex
from mynode import Node
from myresolver import *
from myexceptions import *

class Parser:

    def __init__(self, object: any, printSyntree: bool = False):
        self.object = object
        self.printSyntree = printSyntree
        self.prod = 0

    def execute(self, source: str) -> any:
        self.lex(source)
        self.syn()
        return self.sem()

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
        if not ((len(self.tokens) == 0 or self.expression(self.syntree)) and self.is_end()):
            token = self.next_token()
            raise SyntacticException(f'Token not expected \"{token.value}\" in position {token.pos}')
        if self.printSyntree:
            self.print_syn()
        
    def sem(self):
        if len(self.tokens) > 0:
            return self.syntree.eval(self.object)
        return None

    '''
    EXPRESSION  -> <TERM> + <EXPRESSION> | <TERM> - <EXPRESSION> | <TERM>
    TERM        -> <FACTOR> * <TERM> | <FACTOR> / <TERM> | <FACTOR>
    FACTOR      -> <VARIABLE> | <LITERAL> | ( <EXPRESSION> )
    VARIABLE    -> <IDENTIFIER> . <VARIABLE> | <IDENTIFIER>    
    IDENTIFIER  -> <FUNCTION> | <PROPERTY>    
    FUNCTION    -> ID ( PARAMETERS )
    PROPERTY    -> ID
    PARAMETERS  -> <EXPRESSION>, <PARAMETERS> | <EXPRESSION> | &
    LITERAL     -> NUMBER | STRING | <BOOL>
    BOOL        -> true | false    
    '''

    def expression(self, parent: Node) -> bool:
        start = self.pos
        node_left = self.create_node(Token(TokenType.NONE, 'LEFT', start))
        node_oper = self.create_node(Token(TokenType.NONE, 'OPER', start), resolvers[ResolverType.OPERATOR])
        node_right = self.create_node(Token(TokenType.NONE, 'RIGHT', start))
        result = (
            ((self.term(node_left) and self.terminator(TokenType.ARIT_OPERATOR, '+', node_oper) and self.expression(node_right) and self.end(1)) or self.reset(start)) or
            ((self.term(node_left) and self.terminator(TokenType.ARIT_OPERATOR, '-', node_oper) and self.expression(node_right) and self.end(2)) or self.reset(start)) or
            ((self.term(node_left) and self.end(3)) or self.reset(start))
        )
        if result:
            if self.prod == 3:
                parent.copy(node_left)
            else:    
                # link operator with operations
                node_oper.clear_children()
                node_oper.add_child(node_left)
                node_oper.add_child(node_right)
                parent.clear_children()
                parent.add_child(node_oper)
        return result
    
    def term(self, parent: Node) -> bool:
        start = self.pos
        node_left = self.create_node(Token(TokenType.NONE, 'LEFT', start))
        node_oper = self.create_node(Token(TokenType.NONE, 'OPER', start), resolvers[ResolverType.OPERATOR])
        node_right = self.create_node(Token(TokenType.NONE, 'RIGHT', start))
        result = (
            ((self.factor(node_left) and self.terminator(TokenType.ARIT_OPERATOR, '*', node_oper) and self.term(node_right) and self.end(1)) or self.reset(start)) or
            ((self.factor(node_left) and self.terminator(TokenType.ARIT_OPERATOR, '/', node_oper) and self.term(node_right) and self.end(2)) or self.reset(start)) or
            ((self.factor(node_left) and self.end(3)) or self.reset(start))
        )
        if result:
            if self.prod == 3:
                parent.copy(node_left)
            else:    
                # link operator with operations
                node_oper.clear_children()
                node_oper.add_child(node_left)
                node_oper.add_child(node_right)
                # link parent with operator
                parent.clear_children()
                parent.add_child(node_oper)
        return result

    def factor(self, parent: Node) -> bool:
        start = self.pos
        node = self.create_node(Token(TokenType.NONE, 'FACTOR', start))
        result = (
            ((self.variable(node) and self.end(1)) or self.reset(start)) or
            ((self.literal(node) and self.end(2)) or self.reset(start)) or
            ((self.terminator(TokenType.DELIMITER, '(') and self.expression(node) and self.terminator(TokenType.DELIMITER, ')') and self.end(3)) or self.reset(start))
        )
        if result:
            if self.prod == 3:
                parent.copy(node)
            else:      
                parent.copy(node)
        return result

    def variable(self, parent: Node) -> bool:
        start = self.pos
        node_left = self.create_node(Token(TokenType.NONE, 'LEFT', start), resolvers[ResolverType.PROPERTY])
        node_right = self.create_node(Token(TokenType.NONE, 'RIGHT', start), resolvers[ResolverType.PROPERTY])
        result = (
            ((self.identifier(node_left) and self.terminator(TokenType.DELIMITER, '.') and self.variable(node_right) and self.end(1)) or self.reset(start)) or
            ((self.identifier(node_left) and self.end(2)) or self.reset(start))
        )
        if result:
            if self.prod == 2:
                parent.copy(node_left)
            else:    
                # link operator with operations
                if node_right.token.value == 'RIGHT':
                    node_left.add_child(node_right.children[0])
                else:
                    node_left.add_child(node_right)
                parent.add_child(node_left)
        return result

    def identifier(self, parent: Node) -> bool:
        start = self.pos
        return (
            ((self.function(parent) and self.end(1)) or self.reset(start)) or
            ((self.property(parent) and self.end(2)) or self.reset(start))
        )
    
    def function(self, parent: Node) -> bool:
        start = self.pos
        node_method = self.create_node(Token(TokenType.NONE, 'METHOD', start), resolvers[ResolverType.METHOD])
        node_param = self.create_node(Token(TokenType.NONE, 'PARAM', start))
        result = (
            ((self.terminator(TokenType.ID, None, node_method) and self.terminator(TokenType.DELIMITER, '(') and self.parameters(node_param) and self.terminator(TokenType.DELIMITER, ')')) or self.reset(start))
        )
        if result:
            parent.copy(node_method)
            parent.add_child(node_param)
        return result

    def property(self, parent: Node) -> bool:
        start = self.pos
        result = (
            ((self.terminator(TokenType.ID)) or self.reset(start))
        )
        if result:
            parent.resolver = resolvers[ResolverType.PROPERTY]
            parent.token = self.tokens[start]
        return result

    def parameters(self, parent: Node) -> bool:
        start = self.pos 
        node_left = self.create_node(Token(TokenType.NONE, 'PARAM1', start))
        node_right = self.create_node(Token(TokenType.NONE, 'PARAM2', start))
        result = (
            ((self.expression(node_left) and self.terminator(TokenType.DELIMITER, ',') and self.parameters(node_right) and self.end(1)) or self.reset(start)) or
            ((self.expression(node_left) and self.end(2)) or self.reset(start)) or
            ((self.end(3)))
        )
        if result:
            if self.prod == 1:
                parent.add_child(node_left)
                parent.add_child(node_right.children[0])
            elif self.prod == 2:
                parent.add_child(node_left)
        return result

    def literal(self, parent: Node) -> bool:
        start = self.pos
        node = self.create_node(self.tokens[start], resolvers[ResolverType.LITERAL])
        result = (
            ((self.number()) or self.reset(start)) or
            ((self.string()) or self.reset(start)) or
            ((self.bool()) or self.reset(start))
        )
        if result:
            parent.copy(node)
        return result

    def number(self) -> bool:
        start = self.pos
        return (
            ((self.terminator(TokenType.NUMBER)) or self.reset(start))
        )

    def string(self) -> bool:
        start = self.pos
        return (
            ((self.terminator(TokenType.STRING)) or self.reset(start))
        )

    def bool(self) -> bool:
        start = self.pos
        return (
            ((self.terminator(TokenType.RESERVED, 'true')) or self.reset(start)) or
            ((self.terminator(TokenType.RESERVED, 'false')) or self.reset(start))
        )

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
        child = self.create_node(Token(TokenType.ID, value, 0))
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
