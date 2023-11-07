from enum import Enum

class Token:

    def __init__(self, type: Enum, value: str, pos: int):
        self.type = type
        self.value = value
        self.pos = pos 

    def __str__(self):
            return f"Token(type='{self.type}', value='{self.value}', pos={self.pos})"
