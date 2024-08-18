import json
from scanner import the_lexer, T_group
from CodeGen.CMinusGenerator import CodeGenerator
from Parse_tree import *
from CodeGen.SemanticException import SemanticException
from dataclasses import dataclass

class LL1:
    def __init__(self, first_sets, follow_sets, products_sets, augmented_product_sets):
        self.first_sets = first_sets
        self.follow_sets = follow_sets
        self.products_sets = products_sets
        self.augmented_product_sets = augmented_product_sets

        self.terminals = [x for x in self.first_sets if x not in self.follow_sets]
        self.terminals.remove("\u03b5")
        self.terminals.append('/')
        self.terminals.append('EOF')

        self.table = {x: ['0' for _ in range(len(self.terminals))] for x in self.follow_sets}
        
    def create_table(self):
        for k in self.products_sets:
            
            rhs, lhs, _ = self.products_sets[k]

            map_terminals = []
            need_follows = False
            for i in range(len(lhs)):
                X = lhs[i]
                for f in self.first_sets[X]:
                    if f != "\u03b5" and f not in map_terminals:
                        map_terminals.append(f)

                if "\u03b5" not in self.first_sets[X]:
                    break
                elif i == len(lhs) - 1 and "\u03b5" in self.first_sets[X]:
                    need_follows = True

            if need_follows:
                for fo in self.follow_sets[rhs]:
                    if fo not in map_terminals:
                        map_terminals.append(fo)

            for terminal in map_terminals:
                index = self.terminals.index(terminal)
                self.table[rhs][index] = k

            for fo in self.follow_sets[rhs]:
                index = self.terminals.index(fo)
                if self.table[rhs][index] == '0':
                    self.table[rhs][index] = 'synch'

    def get_result(self, non_terminal, terminal):
        index = self.terminals.index(terminal)
        return self.table[non_terminal][index]
                    
                    



file = open('fi.json', 'r')
first_sets = json.loads(file.read())
file.close()

file = open('fo.json', 'r')
follow_sets = json.loads(file.read())
file.close()

file = open('products_sets.json', 'r')
products_sets = json.loads(file.read())
file.close()

file = open('new_products_sets.json', 'r')
augmented_products_sets = json.loads(file.read())
file.close()

parser = LL1(first_sets, follow_sets, products_sets, augmented_products_sets)
parser.create_table()

actions = []
errors = []
stack = ['Program', 'EOF']
input = the_lexer.get_next_token()
previous_input = None
continue_parser = True

parse_tree = Parse_tree()
code_generator = CodeGenerator()
semantic_errors = []

unexp_eof = False
while continue_parser:
    # print(f'stack: {stack}\tinput:{str(input.token_type.value)}  {input.lexeme} {input.lineno}')
    
    if stack[0].startswith('#'):
        action_symbol = stack[0]
        scopes = code_generator.symbol_table.scopes
        try:
            print(action_symbol)
            print(previous_input.lexeme)
            print(input.lexeme)
            code_generator.act(action_symbol, previous_input, input)
        except SemanticException as e:
            message = f"#{previous_input.lineno}: {e}"
            print(message)
            if len(semantic_errors) == 0:
                semantic_errors.append(message)
            elif semantic_errors[-1] != message or e.error_type != 4:
                semantic_errors.append(message)
        except:
            pass
        stack.pop(0)

    elif stack[0] in parser.terminals:
        if input.token_type == T_group.SYMBOL \
        or input.token_type == T_group.KEYWORD \
        or input.token_type == T_group.START:
            inp = input.lexeme
        else:
            inp = str(input.token_type.value)

        if stack[0] == inp:
            if inp == 'EOF':
                actions.append('accept')
                # print('accept')
                break
            else:
                actions.append(f'terminal {inp}')
                # print(f'terminal {inp}')
                node = parse_tree.nodes.pop(0)
                node.name = f'({str(input.token_type.value)}, {input.lexeme})'
                previous_input = input
                input = the_lexer.get_next_token()
                stack.pop(0)
        else:
            if stack[0] == 'EOF':
                actions.append(f'Exception')
                # print(f'Exception')
                previous_input = input
                input = the_lexer.get_next_token()
            else:
                A = stack.pop(0)
                node = parse_tree.nodes.pop(0)
                parent = node.parent
                parent.childs.remove(node)
                actions.append(f'#{input.lineno} : syntax error, missing {A}')
                errors.append(f'#{input.lineno} : syntax error, missing {A}')
                # print(f'#{input.lineno} : syntax error, missing {A}')

    else:
        if input.token_type == T_group.SYMBOL \
            or input.token_type == T_group.KEYWORD \
                or input.token_type == T_group.START:
            inp = input.lexeme
        else:
            inp = str(input.token_type.value)
        
        act = parser.get_result(stack[0], inp)
        if act == 'synch':
            actions.append(f'#{input.lineno} : syntax error, missing {stack[0]}')
            errors.append(f'#{input.lineno} : syntax error, missing {stack[0]}')
            # print(f'#{input.lineno} : syntax error, missing {stack[0]}')
            stack.pop(0)
            node = parse_tree.nodes.pop(0)
            # delete from parent node
            parent = node.parent
            parent.childs.remove(node)
        elif act == '0':
            if inp == '$':
                actions.append(f'#{input.lineno-1} : syntax error, Unexpected EOF')
                errors.append(f'#{input.lineno-1} : syntax error, Unexpected EOF')
                # print(f'#{input.lineno} : syntax error, Unexpected EOF')
                unexp_eof = True
                break
            else:
                actions.append(f'#{input.lineno} : syntax error, illegal {inp}')
                errors.append(f'#{input.lineno} : syntax error, illegal {inp}')
                # print(f'#{input.lineno} : syntax error, illegal {inp}')
                previous_input = input
                input = the_lexer.get_next_token()
        else:
            actions.append(f'production rule no. {act}')
            # print(f'production rule no. {act}')
            stack.pop(0)
            node = parse_tree.nodes.pop(0)

            sentential_form = parser.augmented_product_sets[act][1]

            # print(f'put {sentential_form}')
            if "\u03b5" in sentential_form:
                child_node = Node('epsilon', node)
                node.add_child(child_node)
                
            else:
                for i in range(len(sentential_form)-1, -1, -1):
                    child_node = Node(sentential_form[i], node)
                    parse_tree.nodes.insert(0, child_node)
                    node.add_child(child_node)
                    stack.insert(0, sentential_form[i])


if len(semantic_errors) == 0:
    result_program = ""
    for lineno, line in enumerate(code_generator.program):
        result_program += f"{lineno}\t{line}"
        result_program += "\n"
    semantic_errors = ["The input program is semantically correct."]
else:
    result_program = "The output code has not been generated."

with open("output.txt", "w", encoding="utf-8") as f:
    print(result_program, file=f)
with open("semantic_errors.txt", "w", encoding="utf-8") as f:
    print("\n".join(semantic_errors), file=f)




if unexp_eof:
    while stack[0] != '$':
        stack.pop(0)
        node = parse_tree.nodes.pop(0)
        parent = node.parent
        parent.childs.remove(node)



