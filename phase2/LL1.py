import json
from compiler2 import the_lexer, T_group
from Parse_tree import *

class LL1:
    def __init__(self, first_sets, follow_sets, products_sets):
        self.first_sets = first_sets
        self.follow_sets = follow_sets
        self.products_sets = products_sets

        self.terminals = [x for x in self.first_sets if x not in self.follow_sets]
        self.terminals.remove("\u03b5")
        self.terminals.append('/')
        self.terminals.append('$')

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

parser = LL1(first_sets, follow_sets, products_sets)
parser.create_table()

actions = []
errors = []
stack = ['Program', '$']
input = the_lexer.get_next_token()
continue_parser = True

parse_tree = Parse_tree()

unexp_eof = False
while continue_parser:
    print(f'stack: {stack}\tinput:{str(input.token_type.value)}  {input.lexeme} {input.lineno}')
    
    
    if stack[0] in parser.terminals:
        if input.token_type == T_group.SYMBOL \
        or input.token_type == T_group.KEYWORD \
        or input.token_type == T_group.START:
            inp = input.lexeme
        else:
            inp = str(input.token_type.value)

        if stack[0] == inp:
            if inp == '$':
                actions.append('accept')
                print('accept')
                break
            else:
                actions.append(f'terminal {inp}')
                print(f'terminal {inp}')
                node = parse_tree.nodes.pop(0)
                node.name = f'({str(input.token_type.value)}, {input.lexeme})'
                input = the_lexer.get_next_token()
                stack.pop(0)
        else:
            if stack[0] == '$':
                actions.append(f'Exception')
                print(f'Exception')
                input = the_lexer.get_next_token()
            else:
                A = stack.pop(0)
                node = parse_tree.nodes.pop(0)
                parent = node.parent
                parent.childs.remove(node)
                actions.append(f'#{input.lineno} : syntax error, missing {A}')
                errors.append(f'#{input.lineno} : syntax error, missing {A}')
                print(f'#{input.lineno} : syntax error, missing {A}')

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
            print(f'#{input.lineno} : syntax error, missing {stack[0]}')
            stack.pop(0)
            node = parse_tree.nodes.pop(0)
            # delete from parent node
            parent = node.parent
            parent.childs.remove(node)
        elif act == '0':
            if inp == '$':
                actions.append(f'#{input.lineno-1} : syntax error, Unexpected EOF')
                errors.append(f'#{input.lineno-1} : syntax error, Unexpected EOF')
                print(f'#{input.lineno} : syntax error, Unexpected EOF')
                unexp_eof = True
                break
            else:
                actions.append(f'#{input.lineno} : syntax error, illegal {inp}')
                errors.append(f'#{input.lineno} : syntax error, illegal {inp}')
                print(f'#{input.lineno} : syntax error, illegal {inp}')
                input = the_lexer.get_next_token()
        else:
            actions.append(f'production rule no. {act}')
            print(f'production rule no. {act}')
            stack.pop(0)
            node = parse_tree.nodes.pop(0)

            sentential_form = parser.products_sets[act][1]

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

if unexp_eof:
    while stack[0] != '$':
        stack.pop(0)
        node = parse_tree.nodes.pop(0)
        parent = node.parent
        parent.childs.remove(node)

cur_list = [parse_tree.start]

def printer(level=0, parse_tree_node= None, is_finish= False, finished_states=[]):
    ret = ""
    if level != 0:
        for i in range(level):
            if i == level - 1:
                if not is_finish:
                    ret += "├── "
                else:
                    ret += "└── "
                    finished_states.append({"node": parse_tree_node, "level": i})
            else:
                is_i_finished = False
                for state in finished_states:
                    temp_node = parse_tree_node
                    while temp_node.parent.name != "Program":
                        if temp_node.parent == state["node"] and i == state["level"]:
                            is_i_finished = True
                            break
                        temp_node = temp_node.parent
                    if is_i_finished:
                        break
                if is_i_finished:
                    ret += "    "
                else:
                    ret += "│   "

        ret += parse_tree_node.name + "\n"
    else:
        ret = parse_tree_node.name + "\n"
    for child_index in range(len(parse_tree_node.childs)):
        if child_index == (len(parse_tree_node.childs) - 1):
            ret += printer(level + 1, parse_tree_node.childs[child_index], True, finished_states)
        else:
            ret += printer(level + 1, parse_tree_node.childs[child_index], False, finished_states)
    return ret

# while len(cur_list) != 0:
#     new_list = []
#     for x in cur_list:
#         print(f'{x.name}', end = '\t')
#         for child in x.childs:
#             new_list.append(child)
#         print()
#     print()
#     cur_list = new_list

# cur_list = [parse_tree.start]
if not unexp_eof:
    cur_list[0].childs.append(Node(name= "$", parent= cur_list[0]))

jafar = (printer(0, cur_list[0], False, []))
file = open("parse_tree.txt", "w")
file.write(jafar[0:(len(jafar)-1)])
file.close()

# for a in actions:
#    print(a)
syntax_error = ''
for e in errors:
    syntax_error = syntax_error + '\n' + e
    print(e)

if len(errors) == 0:
    syntax_error = '\nThere is no syntax error.'

syntax_error = syntax_error[1:]

file = open('syntax_errors.txt', 'w')
file.write(syntax_error)
file.close()



