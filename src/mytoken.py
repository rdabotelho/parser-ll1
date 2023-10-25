from enum import Enum
    
class TokenType(Enum):
    NONE = 0,
    RESERVED = 1,
    ID = 2
    DELIMITER = 3
    ARIT_OPERATOR = 4
    COMP_OPERATOR = 5
    STRING = 6
    NUMBER = 7
    SPACE = 8

token_regex = {    
    TokenType.RESERVED: r'^\b(?:and|or|not|true|false)\b',
    TokenType.ID: r'^[a-zA-Z][a-zA-Z0-9_]*',
    TokenType.DELIMITER: r'^[\(\)\,\.]',
    TokenType.ARIT_OPERATOR: r'^[\+\-\*\/]',
    TokenType.COMP_OPERATOR: r'^[\=\>\<\!]',
    TokenType.STRING: r'^\'(.*?)\'',
    TokenType.NUMBER: r'^\d+(\.\d+)?',
    TokenType.SPACE: r'^\s'
}

class Token:

    def __init__(self, type: TokenType, value: str, pos: int):
        self.type = type
        self.value = value
        self.pos = pos 

    def __str__(self):
            return f"Token(type='{self.type}', value='{self.value}', pos={self.pos})"

