class SemanticException(Exception):
    Messages = [
        "Semantic Error! '{}' is not defined.",
        "Semantic Error! Illegal type of void for '{}'.",
        "Semantic Error! Mismatch in numbers of arguments of '{}'.",
        "Semantic Error! No 'while' found for 'break'.",
        "Semantic Error! Type mismatch in operands, Got {} instead of {}.",
        "Semantic Error! Mismatch in type of argument {} of '{}'. Expected '{}' but got '{}' instead."
    ]
    def __init__(self, error_type, argu):
        message = self.Messages[error_type]
        self.error_type = error_type
        if error_type != 3:
            message = message.format(*argu)
        if error_type == 4:
            message = 'Semantic Error! Type mismatch in operands, Got int instead of array.'
        super().__init__(message)
        self.value = message