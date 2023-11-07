import re
from scanner.token import Token
from commons.exceptions import LexicalException

class Scanner:

    def __init__(self, token_regex: dict, space_type: int):
        self.tokens = []
        self.token_regex = token_regex
        self.space_type = space_type

    def scan(self, source: str) -> list:
        self.tokens = []
        self.pos = 0
        while True:
            token = self.read_token(source) 
            if token:
                if token.type != self.space_type:
                    self.tokens.append(token)
            else:
                break
        return self.tokens

    def read_token(self, sequence: str):
        sub_sequence = sequence[self.pos:]
        for type in list(self.token_regex.keys()):
            match = re.search(self.token_regex[type], sub_sequence)
            if match:
                value = match.group()
                token = Token(type, value, self.pos + 1)
                self.pos += len(value)
                return token
        if len(sub_sequence) > 0:
            raise LexicalException(f'Unidentified token in position {self.pos}')
        return None
    
    def print_tokens(self):
        for token in self.tokens:
            print(token)
