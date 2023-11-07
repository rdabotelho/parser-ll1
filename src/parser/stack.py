from parser.node import Node

class Stack:

    def __init__(self, root: Node):
        self.list = [root]

    def push(self, node: Node):
        self.list.append(node)

    def top(self) -> Node:
        return self.list[-1]
    
    def pop(self) -> Node:
        return self.list.pop()
    
    def print_stack(self):
        s = ''
        for it in self.list:
            s += f'{it.value} '
        print(s)
