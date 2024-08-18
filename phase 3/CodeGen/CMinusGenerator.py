from .InterMediateCode import *
from .SemanticRoutines import SemanticRoutines
from .Symbol import SymbolTable
from .RuntimeStack import RuntimeStack
from .RegisterFile import RegisterFile

class Token:
    def __init__(self, lineno = None, token_type = None, lexeme = None):
        self.lineno =lineno
        self.token_type = token_type
        self.lexeme = lexeme

    def __copy__(self):
        return Token(self.lineno,self.token_type,self.lexeme)

WORD_SIZE = 4


class CodeGenerator:
    def __init__(self):
        self.data_address = 1000
        self.temp_address = 10004
        self.stack_start_address = 10000
        self.program_pointer = 0
        self.semantic_stack = []
        self.data_and_temp_stack = []
        self.function_data_start_pointer = 0
        self.function_temp_start_pointer = 0
        self.program = []
        self.symbol_table = SymbolTable(self)
        self.register_file = RegisterFile(self)
        self.runtime_stack = RuntimeStack(self, self.register_file)
        self.routines = SemanticRoutines(self, self.symbol_table)
        self.jump_to_main_address = 0
        self.initialize()

    def act(self, action, previous_token, current_token):
        action = action[1:]
        if action == 'pid':
            self.routines.pid(previous_token, current_token)
        elif action == 'pnum':
            self.routines.pnum(previous_token)
        elif action == 'jp':
            self.routines.jump()
        elif action == 'jpfSave':
            self.routines.jump_on_false_and_save()
        elif action == 'assign':
            self.routines.assign()
        elif action == 'startRHS':
            self.routines.start_rhs()
        elif action == 'endRHS':
            self.routines.end_rhs()
        elif action == 'label':
            self.routines.label()
        elif action == 'save':
            self.routines.save()
        elif action == 'pop':
            self.routines.pop()
        elif action == 'pushRelopOper':
            self.routines.push_relop_or_operation(previous_token)
        elif action == 'operationExecute':
            self.routines.execute_operation()
        elif action == 'declareArray':
            self.routines.declare_array()
        elif action == 'addressArray':
            self.routines.find_address_of_array_element()
        elif action == 'initializeValue':
            self.routines.initialize_value()
        elif action == 'setArrayType':
            self.routines.set_array_type()
        elif action == 'argumentListHead':
            self.routines.argument_list_head()
        elif action == 'argumentListTail':
            self.routines.argument_list_tail()
        elif action == 'until':
            self.routines.until()
        elif action == 'while':
            self.routines.while_routine()
        elif action == 'break':
            self.routines.add_break()
        elif action == 'startBreakScope':
            self.routines.start_break_scope()
        elif action == 'jpBreak':
            self.routines.push_break_jump()
        elif action == 'declareFunction':
            self.routines.declare_function()
        elif action == 'newScope':
            self.routines.open_new_scope()
        elif action == 'closeScope':
            self.routines.close_scope()
        elif action == 'setFunctionScopeFlag':
            self.routines.set_function_scope_flag()
        elif action == 'popParam':
            self.routines.pop_param(previous_token)
        elif action == 'functionCall':
            self.routines.call_function()
        elif action == 'setReturnValue':
            self.routines.save_return_value()
        elif action == 'jpBack':
            self.routines.jump_back()
        elif action == 'incrementArgumentCount':
            self.routines.increment_argument_count()
        elif action == 'saveType':
            self.routines.save_type(previous_token)
        elif action == 'checkType':
            self.routines.check_type(current_token)
        elif action == 'voidCheck':
            self.routines.void_check()
        elif action == 'setVoidCheckFlag':
            self.routines.set_void_check_flag()
        elif action == 'setPushFlag':
            self.routines.set_push_flag()
        elif action == 'resetPushFlag':
            self.routines.reset_push_flag()
        elif action == 'setCheckDeclarationFlag':
            self.routines.set_check_declaration_flag()
        elif action == 'resetCheckDeclarationFlag':
            self.routines.reset_check_declaration_flag()
        elif action == 'setForceDeclarationFlag':
            self.routines.set_force_declaration_flag()
        elif action == 'resetForceDeclarationFlag':
            self.routines.reset_force_declaration_flag()
        else:
            print('Invalid Action Symbol!', action)

    def initialize(self):
        self.push_instruction(Assign(f"#{self.stack_start_address}", self.register_file.stack_pointer_register_address))
        self.push_instruction(Assign("#0", self.register_file.return_address_register_address))
        self.push_instruction(Assign("#0", self.register_file.return_value_register_address))

        self.jump_to_main_address = len(self.program)
        self.program.append(None)
        self.program_pointer += 1

        self.act('#pid', Token(lexeme='output'), None)
        self.act('#declareFunction', None, None)
        self.act('#newScope', None, None)
        self.act('#setFunctionScopeFlag', None, None)
        self.act('#pid', Token(lexeme="x"), None)
        self.act('#popParam', None, None)
        self.act('#pid', Token(lexeme="x"), None)
        self.act('#newScope', None, None)
        self.push_instruction(Print(self.semantic_stack.pop()))
        self.act('#closeScope', None, None)
        self.act('#jpBack', None, None)

    def insert_instruction(self, instruction, destination):
        if type(destination) == str:
            if destination[0] == "#":
                destination = destination[1:]
            destination = int(destination)
        self.check_program_size(destination)
        self.program[destination] = instruction.to_code()

    def push_instruction(self, instruction):
        self.check_program_size()
        self.program[self.program_pointer] = instruction.to_code()
        self.program_pointer += 1

    def check_program_size(self, size=None):
        if not size:
            size = self.program_pointer
        if type(size) == str:
            if size[0] == "#":
                size = size[1:]
            size = int(size)
        while len(self.program) <= size:
            self.program.append(None)

    def push_list_of_instructions(self, instructions):
        for instruction in instructions:
            self.push_instruction(instruction)

    def next_data_address(self, size=WORD_SIZE):
        address = self.data_address
        self.data_address += size
        return address

    def next_temp_address(self, size=WORD_SIZE):
        address = self.temp_address
        self.temp_address += size
        return address
