class LexicalException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class SyntacticException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class SemanticException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
