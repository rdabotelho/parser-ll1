def parse(input_string):
    # Adicionando o símbolo de fim de cadeia ($) ao final da entrada
    input_string += '$'
    
    # Definindo a tabela de análise (cole a tabela gerada aqui)
    parsing_table = {
        ('S', 'a'): 'AaB',
        ('A', 'b'): 'b',
        ('A', 'c'): '',
        ('A', 'd'): '',
        ('A', '$'): '',
        ('B', 'c'): 'c',
        ('B', 'd'): 'd'
    }
    
    # Pilha de análise
    stack = ['S']
    
    # Índice para percorrer a entrada
    input_index = 0
    
    while stack:
        # Topo da pilha
        top = stack[-1]
        
        if top in parsing_table and input_string[input_index] in parsing_table[top]:
            # Obtemos a produção a partir da tabela
            production = parsing_table[top][input_string[input_index]]
            
            # Se a produção for uma string vazia, apenas a removemos da pilha
            if production != '':
                stack.pop()  # Remove o topo da pilha
                for symbol in reversed(production):
                    stack.append(symbol)  # Adiciona a produção na pilha
            else:
                stack.pop()  # Remove o topo da pilha
        else:
            print("Erro de análise sintática!")
            return
        
        # Avança para o próximo símbolo de entrada
        input_index += 1
    
    print("Análise sintática bem-sucedida!")

# Exemplo de uso
parse("abc$")
