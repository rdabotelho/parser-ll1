def add(list: list, it: str):
    if not it in list:
        list.append(it)

def get_nterms(gram: dict) -> list:
    return list(gram.keys())

def get_terms(gram: dict) -> list:
    result = []
    for nterm in get_nterms(gram):
        prods = gram[nterm]
        for prod in prods:
            for it in prod:
                if not it.isupper():
                    add(result, it)
    result.append('$')
    if 'ε' in result:
        result.remove('ε')
    return result

def get_firsts(gram: dict, nterms: list) -> dict:
    result = {}
    for term in nterms:
        result[term] = first(term, gram)
    return result

def get_follows(gram: dict, nterms: list, firsts: dict) -> dict:
    result = {}
    for nterm in nterms:
        result[nterm] = follow(nterm, gram, firsts)
    return result

def get_table(gram: dict, nterms: list, terms: list, firsts: dict, follows: dict) -> list:
    result = []
    header = ['']
    for term in terms:
        header.append(term)
    result.append(header)
    # For each not terminal
    for nterm in nterms:
        row = [nterm]
        result.append(row)
        for term in terms:
            row.append([])
        # Get the all productions of this not terminal
        prods = gram[nterm]
        # Get the set of firsts of this not terminal
        firstsNTerm = firsts[nterm]
        # Get the set of follows of this not terminal
        followsNTerm = follows[nterm]
        # For each production of this not terminal
        for prod in prods:
            # For each terminal in the set of firsts
            for term in firstsNTerm:
                if term == 'ε':
                    continue
                index = header.index(term)
                # If this production derive the terminal, then add it in the cell
                if is_prod_derive_term(prod, firsts, term):
                    if len(row[index]) > 0:
                        raise RuntimeError(f'Table cell ({nterm}, {term}) cannot have two productions. Review the grammar!')
                    row[index] = prod
            # For each terminal in the set of follows
            for term in followsNTerm:
                index = header.index(term)
                # If this production derive the lambda, then add it in the cell
                if is_prod_derive_term(prod, firsts, 'ε'):
                    if len(row[index]) > 0:
                        raise RuntimeError(f'Table cell ({nterm}, {term}) cannot have two productions. Review the grammar!')
                    row[index] = prod
    return result

def is_prod_derive_term(prod: list, firsts: dict, term: str) -> bool:
    item0 = None
    if len(prod) > 0:
        item0 = prod[0]
    if item0 != None:
        if item0.isupper():
            if term in firsts[item0]:
                return True
        elif item0 == term:
            return True
    return False

def first(X: str, gram: dict):
    result = []
    prods = gram[X]
    for prod in prods:
        # 1. If X -> ε, then first(X) = {ε,..}
        if 'ε' in prod:
            add(result, 'ε')
        for Y in prod:
            if Y.isupper():
                # 2. If X -> YB, then first(X) = first(Y)
                firstY = first(Y, gram)
                for it in firstY:
                    add(result, it)
                # 3. If first(Y) contains ε, then first(X) = first(Y) U first(B)
                if not 'ε' in firstY:
                    break
            else:
                # 4. If X -> aB, then first(X) = {a,..}
                add(result, Y)
                break
    return result

def follow(X: str, gram: dict, firsts: dict):
    result = []
    nterms = list(gram.keys())
    for S in nterms:
        prods = gram[S]
        for prod in prods:
            size = len(prod)
            for i in range(size):
                Y = prod[i]
                if Y == X:
                    nextY = None
                    if i < (size - 1):
                        nextY = prod[i+1]
                    if nextY != None:
                        if nextY.isupper():
                            # 1. For S -> YB, follow(Y) = first(B)
                            firstNextY = firsts[nextY]
                            for it in firstNextY:
                                if it != 'ε':
                                    add(result, it)
                            if 'ε' in firstNextY:
                                # 2. For S -> YB, follow(Y) = first(B) U follow(S), if first(B) contains ε
                                followS = follow(S, gram, firsts)
                                for it in followS:
                                    add(result, it)
                        else:
                            # 3. For S -> Ya, follow(Y) = {..,a}
                            add(result, nextY)
                    elif S != X:
                        # 4. For S -> BY, follow(Y) = follow(S)
                        followS = follow(S, gram, firsts)
                        for it in followS:
                            add(result, it)
    if nterms[0] == X:
        add(result, '$')
    return result

def print_table(table: list):
    s = ''
    for col in table[0]:
        s += '-' * 20
    print(s)
    first = True
    for row in table:
        s = ''
        for col in row:
            t = f'{col}'
            s += t.ljust(20)
        print(s)     
        if first:
            s = ''
            for col in table[0]:
                s += '-' * 20
            print(s)
            first = False

def find_in_table(table: list, nterm: str, term: str) -> list:
    term_row = table[0]
    index = term_row.index(term)
    if not (index > 0):
        return []
    for row in table:
        if row[0] == nterm:
            return row[index]
    return []

class Node:
    
    def __init__(self, value: str, parent: any = None):
        self.value = value
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

    def __str__(self):
        return f"Node(value='{self.value}')"        

class Stack:

    def __init__(self, root: Node):
        self.list = [root]

    def push(self, node: Node):
        self.list.append(node)

    def top(self) -> Node:
        return self.list[-1]
    
    def pop(self) -> Node:
        return self.list.pop()

def parser_ll1(tokens: list, table: list) -> Node:
    stack = Stack(Node('$'))
    stack.push(Node(table[1][0], stack.top()))
    pos = 0
    words = list(tokens)
    words.append('$')
    while True:
        # get the top of stack
        top = stack.top()
        # get the word of lookahead
        lookahead = words[pos]
        # check if is the end
        if lookahead == top.value == '$':
            print('accept')
            break
        # check if the terminal is igual the terminal of top
        if lookahead == top.value:
            stack.pop()
            pos += 1
        # if is not terminal, then find the produtions in the table
        else:
            prod = find_in_table(table, top.value, lookahead)
            # if there is not production, then throw a syntactic error
            if len(prod) == 0:
                print("syntactic error")
                break     
            # if there is production, then remove the not terminal of the stack   
            stack.pop()
            # if there is not ε in the production, then add production in the stack
            if prod[0] != 'ε':
                for it in reversed(prod):
                    stack.push(Node(it, top))
    return stack.top()

def print_syn_tree(node: Node = None, level: int = 0) -> bool:
    print("  " * level + str(node))
    for child in node.children:
        print_syn_tree(child, level + 1)

# EXAMPLE OF USE

# grammar for a expression
gram: dict = {
    "E": [["T", "E2"]],
    "E2": [["+", "T", "E2"],["ε"]],
    "T": [["F", "T2"]],
    "T2": [["*", "F", "T2"],["ε"]],
    "F": [["id"],["(", "E", ")"]]
}

# grammar for a list
#gram: dict = {
#    "L1": [["IT", "L2"], ['ε']],
#    "L2": [[".", "IT", "L2"], ["ε"]],
#    "IT": [["id"]]
#}

# simple grammar
#gram: dict = {
#    "S": [["(", "S", ")"], ['ε']]
#}

if __name__ == "__main__":
    nterms = get_nterms(gram)
    terms = get_terms(gram)
    firsts = get_firsts(gram, nterms) 
    follows = get_follows(gram, nterms, firsts)
    table = get_table(gram, nterms, terms, firsts, follows)

    print(f'nterm: {nterms}')
    print(f'term: {terms}')
    print(f'firsts: {firsts}')
    print(f'follows: {follows}')
    
    print_table(table)

    tokens = ['id','+','id']
    tree = parser_ll1(tokens, table)
    print_syn_tree(tree)
