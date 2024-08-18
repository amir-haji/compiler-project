class Token:
    def __init__(self, lineno=None, token_type=None, lexeme=None):
        self.lineno = lineno
        self.token_type = token_type
        self.lexeme = lexeme