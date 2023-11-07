from scanner.token import Token
from parser.ll1_utils import is_term

class Node:

    def __init__(self, value: str, parent: any = None):
        self.value = value
        self.token = None
        self.children = []
        self.parent = None
        if parent != None:
           parent.add_child(self)

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    def remove_child(self, child):
        child.parent = None
        self.children.remove(child)

    def find_child(self, value: str) -> any:
        for child in self.children:
            if child.value == value:
                return child
        return None
    
    def get_root(self) -> any:
        if self.parent == None:
            return self
        else:
            return self.parent.get_root()
        
    def get_nodes(self, value: str) -> any:
        result = []
        if self.value == value:
            result.append(self)
        else:
            for child in self.children:
                for it in child.get_nodes(value):
                    result.append(it)
        return result
    
    def get_child(self, index: int) -> any:
        return self.children[index]
        
    def is_terminal(self) -> bool:
        return is_term(self.value)
        
    def match(self, token: Token) -> bool:
        return self.is_terminal() and self.value == token.type.name

    def __str__(self):
        return f"Node(value='{self.value}', token={self.token})"   
