from .InterMediateCode import *

WORD_SIZE = 4

class RuntimeStack:
    def __init__(self, codegen: "CodeGen", register_file: "RegisterFile"):
        self.codegen = codegen
        self.register_file = register_file

    def push(self, data):
        # SP shows last full cell
        instructions = [
            Sub(self.register_file.stack_pointer_register_address, f"#{WORD_SIZE}",
                self.register_file.stack_pointer_register_address),
            Assign(data, f"@{self.register_file.stack_pointer_register_address}"),
        ]
        self.codegen.push_list_of_instructions(instructions)

    def pop(self, address):
        instructions = [
            Assign(f"@{self.register_file.stack_pointer_register_address}", address),
            Add(self.register_file.stack_pointer_register_address, f"#{WORD_SIZE}",
                self.register_file.stack_pointer_register_address),
        ]
        self.codegen.push_list_of_instructions(instructions)
