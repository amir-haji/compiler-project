from CodeGen.SemanticException import SemanticException

class Symbol:
    def __init__(self, address=None, lexeme=None, symbol_type=None, size=0, param_count=0):
        self.address = address
        self.lexeme = lexeme
        self.symbol_type = symbol_type
        self.size = size
        self.param_count = param_count
        self.param_symbols = []
        self.is_initialized = False
        self.is_function = False
        self.is_array = False

class SymbolTable:
    def __init__(self, codegen: "CodeGen"):
        self.scopes = [[]]
        self.codegen = codegen

    def find_address(self, lexeme, check_declaration=False, force_declaration=False):
        return self.find_symbol(lexeme, check_declaration, force_declaration).address

    def find_symbol(self, lexeme, check_declaration=False, force_declaration=False, prevent_add=False):
        address = -1
        result_symbol = None
        if not force_declaration:
            for scope in reversed(self.scopes):
                for symbol in reversed(scope):
                    if symbol.lexeme == lexeme:
                        address = symbol.address
                        result_symbol = symbol
                        break
                if result_symbol:
                    break
        if address == -1 and not prevent_add:
            if check_declaration:
                raise SemanticException(0, [lexeme])
            address = self.codegen.next_data_address()
            result_symbol = self.add_symbol(lexeme=lexeme, address=address)
        return result_symbol

    def find_symbol_by_address(self, address):
        result_symbol = None
        for scope in self.scopes[::-1]:
            for symbol in scope:
                if symbol.address == address:
                    result_symbol = symbol
                    break
        return result_symbol

    def add_symbol(self, lexeme, address):
        symbol = Symbol(lexeme=lexeme, address=address)
        self.scopes[-1].append(symbol)
        return symbol

    def remove_symbol(self, lexeme):
        i = 0
        is_found = False
        for symbol in self.scopes[-1]:
            if symbol.lexeme == lexeme:
                is_found = True
                break
            i += 1
        if is_found:
            self.scopes[-1].pop(i)
