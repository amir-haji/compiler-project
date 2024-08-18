

class Utility:
    char_index = -1
    @staticmethod
    def write_tokens(tokens, line_number):
        output = open("lexer/tokens.txt", "r").read()
        output += f"{line_number}"
        for token in tokens:
            output += f"({str(token.token_type.value)},{token.lexeme})"
        output += "\n"
        file = open("lexer/tokens.txt", "w")
        file.write(output)
        file.close()


    @staticmethod
    def read_input_file():
        file = open("lexer/input.txt", "r")
        content = file.read()
        file.close()
        return (content + 'آ')

    @staticmethod
    def write_lexical_errors(error, error_message, line_number):
        output = open("lexer/lexical_errors.txt", "r").read()
        output += f"{line_number} ({error}, {error_message})\n"
        file = open("lexer/lexical_errors.txt", "w")
        file.write(output)
        file.close()

    @staticmethod
    def write_symbol_file(symbol):
        content = open("lexer/symbol_table.txt", "r").read()
        symbols = content.split("\n")
        output = content + f"{len(symbols)}\t{symbol}\n"
        file = open("lexer/symbol_table.txt", "w")
        file.write(output)
        file.close()
    
    def get_next_char(self, content):
        self.char_index += 1
        return content[self.char_index]

    def retreat(self):
        self.char_index -= 1