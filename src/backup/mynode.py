from mytoken import Token, TokenType

class Node:
    def __init__(self, token: Token, parent: any = None):
        self.token = token
        self.children = []
        self.resolver = None
        if parent != None:
            parent.add_child(self)
        self.session = None

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    def remove_child(self, child):
        child.parent = None
        self.children.remove(child)

    def clear_children(self):
        self.children.clear()

    def last_child(self):
        last = self.children[-1]
        if (last != None) and (len(last.children) > 0):
            return last.last_child()
        return last

    def eval(self, object: any) -> any:
        resolver = self.resolver
        if resolver == None:
            return self.evalChildren(object)
        else:
            resolver.sem(self, object)
            return resolver.eval(self, object)

    def evalChildren(self, object: any) -> any:
        result = object
        for child in self.children:
            if child.token.type != TokenType.NONE:
                result = child.eval(object)
        return result
    
    def evalParam(self, index: int, context: any = None) -> any:
        nodeParam = self.children[0]        
        return nodeParam.children[index].eval(self.session)

    def paramCount(self) -> int:
        if len(self.children) == 0:
            return 0
        else:
            nodeParam = self.children[0]
            return len(nodeParam.children)
    
    def copy(self, node: any):
        self.token = node.token
        self.resolver = node.resolver
        self.children = node.children

    def __str__(self):
        if self.resolver == None:            
            resolverType = ''
        else:
            resolverType = self.resolver.type
        return f"Node(type='{self.token.type}', value='{self.token.value}', resolver={resolverType}, pos={self.token.pos})"