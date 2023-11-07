from enum import Enum
    
class TokenType(Enum):
    NONE = 0
    NOT_TERM = 1
    DELIMITER = 2
    ARROW = 3
    BREAK = 4
    SPACE = 5
    TERM = 6

token_regex = {    
    TokenType.NOT_TERM: r'^<([a-zA-Z][a-zA-Z0-9_]*)>',
    TokenType.ARROW: r'^(->)',
    TokenType.DELIMITER: r'^[\|]',
    TokenType.BREAK: r'^\n',
    TokenType.SPACE: r'^\s',
    TokenType.TERM: r'^(([a-zA-Z][a-zA-Z0-9_]*)|.)'
}

class Token:

    def __init__(self, type: TokenType, value: str, pos: int):
        self.type = type
        self.value = value
        self.pos = pos 

    def __str__(self):
            return f"Token(type='{self.type}', value='{self.value}', pos={self.pos})"

