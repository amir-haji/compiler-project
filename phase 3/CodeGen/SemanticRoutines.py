from .Symbol import SymbolTable, Symbol
from .InterMediateCode import *


WORD_SIZE = 4

from CodeGen.SemanticException import SemanticException

class Token:
    def __init__(self, lineno = None, token_type = None, lexeme = None):
        self.lineno =lineno
        self.token_type = token_type
        self.lexeme = lexeme

    def __copy__(self):
        return Token(self.lineno,self.token_type,self.lexeme)

class SemanticRoutines:
    def __init__(self, codegen, symbol_table):
        self.codegen = codegen
        self.symbol_table = symbol_table
        self.argument_counts = []
        self.current_declared_function_symbol = None
        self.is_rhs = False
        self.current_type = None
        self.called_functions = []
        self.breaks = []
        self.has_reached_main = False
        self.current_id = ""
        self.void_flag = False
        self.found_arg_type_mismtach = []
        self.no_push_flag = False
        self.check_declaration_flag = False
        self.function_scope_flag = False
        self.force_declaration_flag = False

    def pid(self, previous_token: Token, current_token: Token):
        self.current_id = previous_token.lexeme
        address = self.symbol_table.find_address(previous_token.lexeme, self.check_declaration_flag,
                                                 self.force_declaration_flag)
        self.find_main_function(previous_token)
        if not self.no_push_flag:
            self.codegen.semantic_stack.append(address)
        self.check_operand_mismatch_error(current_token)
        self.check_arg_mismatch_error(current_token, previous_token)

    def pnum(self, previous_token: Token):
        num = f"#{previous_token.lexeme}"
        if not self.no_push_flag:
            self.codegen.semantic_stack.append(num)
        if len(self.argument_counts) > 0:
            index = self.argument_counts[-1]
            symbol: Symbol = self.symbol_table.find_symbol(self.called_functions[-1], prevent_add=True)
            param_symbol: Symbol = symbol.param_symbols[index]
            if param_symbol.symbol_type == 'array':
                self.raise_arg_type_mismatch_error(index + 1, symbol.lexeme, 'array', 'int')

    def jump(self):
        instruction = JP(f"#{self.codegen.program_pointer}")
        destination = self.codegen.semantic_stack.pop()
        self.codegen.insert_instruction(instruction, destination)

    def jump_on_false_and_save(self):
        destination = self.codegen.semantic_stack.pop()
        condition = self.codegen.semantic_stack.pop()
        self.codegen.insert_instruction(JPF(condition, f"#{self.codegen.program_pointer + 1}"), destination)
        self.codegen.semantic_stack.append(f"#{self.codegen.program_pointer}")
        self.codegen.program_pointer += 1

    def assign(self):
        value = self.codegen.semantic_stack.pop()
        address = self.codegen.semantic_stack.pop()
        self.codegen.push_instruction(Assign(value, address))
        self.codegen.semantic_stack.append(value)
        symbol: Symbol = self.codegen.symbol_table.find_symbol_by_address(address)
        if symbol:
            symbol.is_initialized = True

    def start_rhs(self):
        self.is_rhs = True

    def end_rhs(self):
        self.is_rhs = False

    def label(self):
        self.codegen.semantic_stack.append(f"#{self.codegen.program_pointer}")

    def save(self):
        self.codegen.semantic_stack.append(f"#{self.codegen.program_pointer}")
        self.codegen.program_pointer += 1

    def pop(self):
        self.codegen.semantic_stack.pop()

    def push_relop_or_operation(self, previous_token: Token):
        self.codegen.semantic_stack.append(previous_token.lexeme)

    def execute_operation(self):
        temp_address = self.codegen.next_temp_address()
        operand2 = self.codegen.semantic_stack.pop()
        operation = self.codegen.semantic_stack.pop()
        operand1 = self.codegen.semantic_stack.pop()
        self.codegen.semantic_stack.append(temp_address)
        operation_to_instruction = {
            '+': Add,
            '-': Sub,
            '<': LT,
            '==': Eq,
            '*': Mult,
        }
        self.codegen.push_instruction(operation_to_instruction[operation](operand1, operand2, temp_address))

    def declare_array(self):
        length = int(self.codegen.semantic_stack.pop()[1:])
        symbol: Symbol = self.codegen.symbol_table.scopes[-1][-1]
        symbol.is_array = True
        symbol.symbol_type = 'array'
        size = length * WORD_SIZE
        array_start_address = self.codegen.next_data_address(size=size)
        self.codegen.push_instruction(Assign(f"#{array_start_address}", symbol.address))
        if len(self.codegen.symbol_table.scopes) > 1:
            for address in range(array_start_address, array_start_address + size, WORD_SIZE):
                self.codegen.push_instruction(Assign("#0", address))

    def find_address_of_array_element(self):
        offset = self.codegen.semantic_stack.pop()
        temp = self.codegen.next_temp_address()
        array_start = self.codegen.semantic_stack.pop()
        self.codegen.push_list_of_instructions([
            Mult(offset, f"#{WORD_SIZE}", temp),
            Add(temp, f"{array_start}", temp),
        ])
        self.codegen.semantic_stack.append(f"@{temp}")

    def initialize_value(self):
        if len(self.codegen.symbol_table.scopes) > 1:
            symbol: Symbol = self.codegen.symbol_table.scopes[-1][-1]
            if not symbol.is_array:
                symbol.symbol_type = 'int'
                self.codegen.push_instruction(Assign("#0", symbol.address))

    def set_array_type(self):
        symbol: Symbol = self.codegen.symbol_table.scopes[-1][-1]
        symbol.is_array = True
        symbol.symbol_type = 'array'

    def argument_list_head(self):
        self.argument_counts.append(0)
        self.called_functions.append(self.current_id)
        self.found_arg_type_mismtach.append(False)

    def argument_list_tail(self):
        self.found_arg_type_mismtach.pop()

    def until(self):
        condition = self.codegen.semantic_stack.pop()
        destination = self.codegen.semantic_stack.pop()
        self.codegen.push_instruction(JPF(condition, destination))

    def while_routine(self):
        code_destination = self.codegen.semantic_stack.pop()
        condition = self.codegen.semantic_stack.pop()
        destination = self.codegen.semantic_stack.pop()
        self.codegen.insert_instruction(JPF(condition, f'#{self.codegen.program_pointer + 1}'), code_destination)
        self.codegen.push_instruction(JP(destination))
        
        

    def start_break_scope(self):
        self.breaks.append([])

    def add_break(self):
        if not self.breaks:
            raise SemanticException(3, None)
        self.breaks[-1].append(self.codegen.program_pointer)
        self.codegen.program_pointer += 1

    def push_break_jump(self):
        for destination in self.breaks[-1]:
            self.codegen.insert_instruction(JP(f"#{self.codegen.program_pointer}"), destination)
        self.breaks.pop()

    def declare_function(self):
        symbol: Symbol = self.codegen.symbol_table.scopes[-1][-1]
        symbol.address = f"#{self.codegen.program_pointer}"
        symbol.is_function = True
        symbol.symbol_type = self.current_type
        symbol.param_count = 0
        self.current_declared_function_symbol = symbol
        self.void_flag = False
        self.codegen.function_data_start_pointer = self.codegen.data_address
        self.codegen.function_temp_start_pointer = self.codegen.temp_address

    def open_new_scope(self):
        if not self.function_scope_flag:
            self.codegen.symbol_table.scopes.append([])
        self.function_scope_flag = False
        self.codegen.data_and_temp_stack.append((self.codegen.data_address, self.codegen.temp_address))

    def close_scope(self):
        self.codegen.symbol_table.scopes.pop()
        self.codegen.data_address, self.codegen.temp_address = self.codegen.data_and_temp_stack.pop()

    def set_function_scope_flag(self):
        self.function_scope_flag = True

    def increment_argument_count(self):
        self.found_arg_type_mismtach[-1] = False
        self.argument_counts[-1] += 1

    def pop_param(self, previous_token: Token):
        address = self.codegen.semantic_stack.pop()
        self.codegen.runtime_stack.pop(address)
        symbol: Symbol = self.codegen.symbol_table.find_symbol_by_address(address)
        symbol.symbol_type = self.current_type
        if previous_token and previous_token.lexeme == ']':
            symbol.symbol_type = 'array'
            symbol.is_array = True
        self.current_declared_function_symbol.param_symbols.append(symbol)
        if symbol:
            symbol.is_initialized = True
            self.current_declared_function_symbol.param_count += 1

    def call_function(self):
        self.store_machine_states()
        self.codegen.register_file.push_registers()
        arg_count = self.argument_counts.pop()
        self.codegen.register_file.save_return_address(arg_count)
        self.find_args_and_push_jump(arg_count)
        self.codegen.register_file.pop_registers()
        self.restore_machine_states()
        self.retrieve_return_value()
        function_name = self.called_functions.pop()
        symbol = self.codegen.symbol_table.find_symbol(function_name)
        if symbol.param_count != arg_count:
            raise SemanticException(2, [function_name])

    def jump_back(self):
        if not self.has_reached_main:
            self.codegen.push_instruction(JP(self.codegen.register_file.return_address_register_address))

    def save_return_value(self):
        value = self.codegen.semantic_stack.pop()
        self.codegen.register_file.save_return_value(value)

    def save_type(self, previous_token: Token):
        self.current_type = previous_token.lexeme

    def check_type(self, current_token: Token):
        symbol = self.symbol_table.find_symbol(self.current_id, prevent_add=True)
        if symbol.is_array:
            if current_token.lexeme != '[' and not self.argument_counts:
                raise SemanticException(4, ['array', 'int'])

    def void_check(self):
        if self.void_flag:
            self.void_flag = False
            self.codegen.symbol_table.remove_symbol(self.current_id)
            raise SemanticException(1, [self.current_id])

    def set_void_check_flag(self):
        self.void_flag = True

    def set_push_flag(self):
        if not self.function_scope_flag:
            self.no_push_flag = True

    def reset_push_flag(self):
        self.no_push_flag = False

    def set_check_declaration_flag(self):
        self.check_declaration_flag = True

    def reset_check_declaration_flag(self):
        self.check_declaration_flag = False

    def set_force_declaration_flag(self):
        self.force_declaration_flag = True

    def reset_force_declaration_flag(self):
        self.force_declaration_flag = False

    def find_args_and_push_jump(self, arg_count):
        for i in range(arg_count):
            data = self.codegen.semantic_stack.pop()
            self.codegen.runtime_stack.push(data)
        address = self.codegen.semantic_stack.pop()
        self.codegen.push_instruction(JP(address))

    def store_machine_states(self):
        for address in range(self.codegen.function_data_start_pointer, self.codegen.data_address, WORD_SIZE):
            symbol: Symbol = self.codegen.symbol_table.find_symbol_by_address(address)
            if symbol and symbol.is_initialized:
                self.codegen.runtime_stack.push(address)
        for address in range(self.codegen.function_temp_start_pointer, self.codegen.temp_address, WORD_SIZE):
            self.codegen.runtime_stack.push(address)

    def restore_machine_states(self):
        for address in range(self.codegen.temp_address, self.codegen.function_temp_start_pointer, -WORD_SIZE):
            self.codegen.runtime_stack.pop(address - WORD_SIZE)
        for address in range(self.codegen.data_address, self.codegen.function_data_start_pointer, -WORD_SIZE):
            symbol: Symbol = self.codegen.symbol_table.find_symbol_by_address(address - WORD_SIZE)
            if symbol and symbol.is_initialized:
                self.codegen.runtime_stack.pop(address - WORD_SIZE)

    def retrieve_return_value(self):
        temp = self.codegen.next_temp_address()
        self.codegen.semantic_stack.append(temp)
        self.codegen.push_instruction(Assign(self.codegen.register_file.return_value_register_address, temp))

    def find_main_function(self, previous_token):
        if previous_token.lexeme == 'main':
            self.codegen.insert_instruction(JP(f"#{self.codegen.program_pointer}"), self.codegen.jump_to_main_address)
            if not self.has_reached_main:
                for symbol in self.codegen.symbol_table.scopes[0]:
                    if not symbol.is_function:
                        self.codegen.push_instruction(Assign("#0", symbol.address))
            self.has_reached_main = True

    def check_operand_mismatch_error(self, current_token):
        if self.is_rhs:
            symbol = self.symbol_table.find_symbol(self.current_id, prevent_add=True)
            if symbol.is_function:
                if symbol.symbol_type != 'int':
                    raise SemanticException(4, ['void', 'int'])
            else:
                if symbol.is_array:
                    if current_token.lexeme != '[' and not self.argument_counts:
                        raise SemanticException(4, ['array', 'int'])

    def check_arg_mismatch_error(self, current_token, previous_token):
        if len(self.argument_counts) > 0:
            index = self.argument_counts[-1]
            symbol: Symbol = self.symbol_table.find_symbol(self.called_functions[-1], prevent_add=True)
            param_symbol: Symbol = symbol.param_symbols[index]
            current_symbol: Symbol = self.codegen.symbol_table.find_symbol(previous_token.lexeme, prevent_add=True)
            if param_symbol.symbol_type == 'int':
                if current_symbol.symbol_type == 'array' and current_token.lexeme != "[":
                    self.raise_arg_type_mismatch_error(index + 1, symbol.lexeme, 'int', 'array')
                if current_symbol.symbol_type == 'void':
                    self.raise_arg_type_mismatch_error(index + 1, symbol.lexeme, 'int', 'void')
            if param_symbol.symbol_type == 'array':
                if current_symbol.symbol_type == 'int':
                    self.raise_arg_type_mismatch_error(index + 1, symbol.lexeme, 'array', 'int')
                if current_symbol.symbol_type == 'array' and current_token.lexeme == "[":
                    self.raise_arg_type_mismatch_error(index + 1, symbol.lexeme, 'array', 'int')
                if current_symbol.symbol_type == 'void':
                    self.raise_arg_type_mismatch_error(index + 1, symbol.lexeme, 'array', 'void')

    def raise_arg_type_mismatch_error(self, index, lexeme, expected, got):
        if not self.found_arg_type_mismtach or not self.found_arg_type_mismtach[-1]:
            if len(self.found_arg_type_mismtach) == 0:
                self.found_arg_type_mismtach.append(True)
            self.found_arg_type_mismtach[-1] = True
            raise SemanticException(5, [index, lexeme, expected, got])
