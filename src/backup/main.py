from myparser import Parser

class Session:
    def __init__(self, client):
        self.client = client

class Client:
    def __init__(self, first_name, last_name, age, account):
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.account = account

'''
Explicacoes:

Essa tabela de analise sintatica foi feito para o tipo de analise LL(1) (existem outros, como a LR por exemplo).
LL(1) significa que a analise sera feita de cima para baixo (abordagem Top-Down) da esquerda para a direita e diante de um
nao-terminal na pilha, basta 1 proximo simbolo (token ou lookahead) para determinar a proxima producao.

Importante:

Para nao haver problema na geracao da tabela a gramatica nao pode sem ambigua e ter recursao a esquerda.
Deixar somente 1 terminal em cada producao
A gramatica estar fatorada nao e um impeditivo porem facilita a analise.

Para criar a tabela a partir de uma gramatica e necessario calcular o FIRST e FOLLOW dos nao-terminaos.
FIRST(T): Sao os terminais que podem iniciar uma cadeia de producao derivada do nao-terminal T.
FOLLOW(T): Sao osterminais que podem aparecer imediatamente apos o nao-terminal T em uma derivacao.

Regras do FOLLOW:
    1. Se S é o símbolo inicial, então coloque $ em FOLLOW(S).
    2. Se há uma produção S -> aBC, então tudo em FIRST(X) exceto ε está em FOLLOW(B). Se ε está em FIRST(C), então tudo em FOLLOW(S) está em FOLLOW(B).
    3. Se há uma produção A -> aB, então tudo em FOLLOW(A) está em FOLLOW(B).

Example:
Dado a seguinte gramatica:
S -> AaBC
A -> b | ε
B -> c | d
C -> e | ε

FIRST(S): {b,ε}
FIRST(A): {b,ε}
FIRST(B): {c,d}
FIRST(C): {e,ε}

FOLLOW(S): {$}
FOLLOW(A): {a,c,d,e}
FOLLOW(B): {a,c,e}
FOLLOW(C): {a,e}

Tabela:
|       | a       | b       | c       | d       | e       | $       |
|-------|---------|---------|---------|---------|---------|---------|
|   S   |         | AaBC    |         |         |         |         |
|   A   |         | b       |         |         |         |         |
|   B   |         |         | c       | d       |         |         |
|   C   |         |         |         |         | e       | ε       |


Tabela em Python:

parsing_table = {
    ('S', 'a'): 'AaB',
    ('A', 'b'): 'b',
    ('A', 'c'): '',
    ('A', 'd'): '',
    ('A', '$'): '',
    ('B', 'c'): 'c',
    ('B', 'd'): 'd'
}
    
'''

GRAMATIC = '''<A>  -> <E> + <T> | <E> - <T> | <T>
<E>  -> <T> * <F> | <T> / <F> | <F>
<F>  -> ( <E> ) | num'''

if __name__ == "__main__":
    client = Client('Rafael', 'Botelho', 16, '1234')
    session = Session(client)
    
    result = Parser(session, True).execute(GRAMATIC)
    print(result)