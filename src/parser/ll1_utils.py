def add(list: list, it: str):
    if not it in list:
        list.append(it)

def is_term(value: str) -> bool:
    return not (value.startswith('<') and value.endswith('>'))

def is_not_term(value: str) -> bool:
    return not is_term(value)

def get_nterms(gram: dict) -> list:
    return list(gram.keys())

def get_terms(gram: dict) -> list:
    result = []
    for nterm in get_nterms(gram):
        prods = gram[nterm]
        for prod in prods:
            for it in prod:
                if is_term(it):
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
        if is_not_term(item0):
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
            if is_not_term(Y):
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
    # S -> ..X..
    for S in nterms:
        prods = gram[S]
        for prod in prods:
            size = len(prod)
            for i in range(size):
                Y = prod[i]
                if Y == X:
                    nextY = None
                    if i < (size - 1):
                        # get the first production (Ex. eA = e)
                        nextY = prod[i+1]
                    if nextY != None:
                        if is_not_term(nextY):
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
    print(f'follows: {follows}\n')
    
    print('SYNTACTIC ANALYSIS TABLE')
    print_table(table)
    