from enum import Enum

class Panic_states(Enum):
    PANIC_INVALID_INPUT = 'Invalid input'
    PANIC_INVALID_NUMBER = 'Invalid number'
    PANIC_UNCLOSED_COMMENT = 'Unclosed comment'
    PANIC_UNMATCHED_COMMENT = 'Unmatched comment'


class Lexer:

    def __init__(self, content, util, dfa):
        self.lines = {}
        self.dfa = dfa
        self.content = content
        self.util = util
        self.curr_lineno = 1
        self.curr_line = None
        self.char_index = 0
        self.must_continue = True
        self.is_eof = False
        pass

    @staticmethod
    def get_token_type(token_type, lexeme):
        if token_type != T_group.KEYWORD_ID:
            return token_type
        else:
            if lexeme in keywords:
                return T_group.KEYWORD
            return T_group.ID
        
    def get_next_token(self):
        token = self.get_next_token2()

        while token.token_type not in T_group or (token.token_type == T_group.WHITESPACE or token.token_type == T_group.WHITESPACE or token.token_type == T_group.COMMENT):
            token = self.get_next_token2()
            if token.token_type == T_group.START:
                token.lexeme = '$'

        return token

    def get_next_token2(self):
        current_state = self.dfa.states[0]
        lexeme = ""
        start_line = self.curr_lineno
        is_eof_step = False
        exception = False
        while True:
            character = self.util.get_next_char(self.content)
            if character == 'آ':
                try:
                    # print(current_state.num)
                    if current_state.num != 0:
                        exception = True
                        current_state = current_state.move_state("FINISH")
                    is_eof_step = True
                    self.is_eof = True
                    break
                except KeyError:
                    return panic_mode(current_state, lexeme, start_line)
            if character == '\n':
                self.curr_lineno += 1
            lexeme += character
            try:
                current_state = current_state.move_state(character)
                # print(character)
                # print(current_state.num)
            except KeyError:
                return panic_mode(current_state, lexeme, start_line)
            if current_state.is_terminal or current_state.is_panic:
                
                break
        if current_state.is_retreat:
            if not is_eof_step:
                lexeme = lexeme[:-1]
            if character == '\n':
                self.curr_lineno -= 1
            self.util.retreat()
        if (current_state.is_panic and not current_state.num == 0) or (not current_state.is_terminal and exception):
            return panic_mode(current_state, lexeme, start_line)
        token_type = Lexer.get_token_type(current_state.token_group, lexeme)
        return Token(start_line, token_type, lexeme)


def panic_mode(curr_state, lexeme, start_line):
    panic_state = Panic_states.PANIC_INVALID_INPUT
    if curr_state.token_group == T_group.NUM:
        panic_state = Panic_states.PANIC_INVALID_NUMBER
    if curr_state.token_group == T_group.COMMENT:
        if lexeme.startswith('/*'):
            panic_state = Panic_states.PANIC_UNCLOSED_COMMENT
    if curr_state.token_group == T_group.SYMBOL:
        if lexeme.startswith('*/'):
            panic_state = Panic_states.PANIC_UNMATCHED_COMMENT
    if len(lexeme) != 0 and lexeme[-1] in whitespace:
        lexeme = lexeme[:-1]
    return Token(start_line, panic_state, lexeme)



class Utility:
    char_index = -1
    

    is_it_first = True
    @staticmethod
    def write_tokens(tokens, line_number):
        num_token = 0
        for token in tokens:
            if str(token.token_type.value) != 'WHITESPACE' and str(token.token_type.value) != 'COMMENT':
                num_token += 1

        if num_token > 0:
            output = open("tokens.txt", "r").read()
            output += f"{line_number}.\t"
            for token in tokens:
                if str(token.token_type.value) != 'WHITESPACE' and str(token.token_type.value) != 'COMMENT':
                    output += f"({str(token.token_type.value)}, {token.lexeme}) "
            output += "\n"
            file = open("tokens.txt", "w")
            file.write(output)
            file.close()


    @staticmethod
    def read_input_file():
        file = open("input.txt", "rb")
        content = file.read().decode()
        file.close()
        return content + "\nآ"

    @staticmethod
    def write_lexical_errors(error, error_message, line_number, new_line):
        output = open("lexical_errors.txt", "rb").read().decode()
        if new_line and Utility.is_it_first:
            output += f"{line_number}.\t"
            Utility.is_it_first = False
        elif new_line and not Utility.is_it_first:
            output += f"\n{line_number}.\t"
        if len(error) > 6:
            error = error[:6] + ' ...'
        output += f"({error}, {str(error_message.value)}) "
        file = open("lexical_errors.txt", "w", encoding="utf-8")
        file.write(output)
        file.close()

    @staticmethod
    def check_lexical_error():
        content = open("lexical_errors.txt", "rb").read().decode()
        if len(content) == 0:
            file = open("lexical_errors.txt", "w")
            file.write("There is no lexical error.")
            file.close()
        else:
            answer = ""
            for word in content:
                if word != "\r":
                    answer += word
            answer = answer + '\n'
            file = open("lexical_errors.txt", "w", encoding="utf-8")
            file.write(answer)
            file.close()


    @staticmethod
    def write_symbol_file(symbol):
        content = open("symbol_table.txt", "r").read()
        symbols = content.split("\n")
        output = content + f"{len(symbols)}.\t{symbol}\n"
        file = open("symbol_table.txt", "w")
        file.write(output)
        file.close()
    
    def get_next_char(self, content):
        self.char_index += 1
        return content[self.char_index]

    def retreat(self):
        self.char_index -= 1

from enum import Enum

class T_group(Enum):
    KEYWORD = 'KEYWORD'
    KEYWORD_ID = 'KEYWORD_ID'
    SYMBOL = 'SYMBOL'
    WHITESPACE = 'WHITESPACE'
    COMMENT = 'COMMENT'
    ID = 'ID'
    NUM = 'NUM'
    START = 'START'
    FINISH = 'FINISH'
    END = 'END'


class Dfa:
    states = {}
    def __init__(self, num, token_group, is_terminal=False, is_panic=False, is_retreat=False):
        self._transitions = {}
        self.num = num
        self.token_group = token_group
        self.is_terminal = is_terminal
        self.is_panic = is_panic
        self.is_retreat = is_retreat
        Dfa.states[num] = self

    def add_edge(self, dest, character):
        self._transitions[character] = dest

    def move_state(self, character):
        return self._transitions[character]
    

def add_edges(start, dest, c_lists):
    for c_list in c_lists:
        for c in c_list:
            start.add_edge(dest, c)

def exclusion(c_lists):
    new_c_lists = []
    valid = all_valid
    for c_list in c_lists:
        valid = valid.replace(c_list, '')
    new_c_lists.append(valid)
    return new_c_lists

def add_eof_edge(start, dest):
    start.add_edge(dest, 'FINISH')


def initialize_keyword_id_dfa(start):
    s1 = Dfa(1, T_group.KEYWORD_ID)
    s2 = Dfa(1, T_group.KEYWORD_ID, is_terminal=True, is_retreat=True)

    add_edges(start, s1, [letters])
    add_edges(s1, s1, [letters, digits])
    add_edges(s1, s2, exclusion([letters, digits]))
    add_eof_edge(s1, s2)


def initialize_num_dfa(start):
    s3 = Dfa(3, T_group.NUM)
    s4 = Dfa(4, T_group.NUM, is_terminal=True, is_retreat=True)

    add_edges(start, s3, [digits])
    add_edges(s3, s3, [digits])
    add_edges(s3, s4, exclusion([letters, digits]))
    add_eof_edge(s3, s4)

def initialize_symbol_dfa(start):
    s5 = Dfa(5, T_group.SYMBOL, is_terminal=True)
    s6 = Dfa(6, T_group.SYMBOL)
    s7 = Dfa(7, T_group.SYMBOL, is_terminal=True)
    s8 = Dfa(8, T_group.SYMBOL)
    s9 = Dfa(9, T_group.SYMBOL, is_terminal=True, is_retreat=True)

    add_edges(start, s5, [symbol.replace('*', '').replace('=', '')])
    add_edges(start, s6, ['='])
    add_edges(s6, s7, ['='])
    add_edges(s6, s9, exclusion(['=']))
    add_edges(start, s8, ['*'])
    add_edges(s8, s9, exclusion('/'))
    add_eof_edge(s6, s9)
    add_eof_edge(s8, s9)


def initialize_comment_dfa(start):
    s10 = Dfa(10, T_group.COMMENT)
    s11 = Dfa(11, T_group.COMMENT)
    s12 = Dfa(12, T_group.COMMENT, is_terminal=True)
    s13 = Dfa(13, T_group.COMMENT)
    s14 = Dfa(14, T_group.COMMENT)
    s15 = Dfa(15, T_group.SYMBOL, is_terminal=True, is_retreat=True)
    s17 = Dfa(15, T_group.SYMBOL, is_panic=True)

    add_edges(start, s10, ['/'])
    # add_edges(s10, s11, ['/'])
    add_edges(s11, s11, [all_chars.replace('\n', '')])
    add_edges(s11, s12, ['\n'])
    add_eof_edge(s11, s12)
    add_edges(s10, s13, ['*'])
    add_edges(s13, s13, [all_chars.replace('*', '')])
    add_edges(s13, s14, ['*'])
    add_edges(s14, s14, ['*'])
    add_edges(s14, s13, [all_chars.replace('*', '').replace('/', '')])
    add_edges(s14, s12, ['/'])
    add_edges(s10, s15, exclusion(['*']))
    add_eof_edge(s13, s17)

def initialize_whitespace_dfa(start):
    s16 = Dfa(16, T_group.WHITESPACE, is_terminal=True)
    add_edges(start, s16, [whitespace])



def initialize_states():
    start = Dfa(0, T_group.START)
    initialize_keyword_id_dfa(start)
    initialize_num_dfa(start)
    initialize_symbol_dfa(start)
    initialize_comment_dfa(start)
    initialize_whitespace_dfa(start)
    return start

class Token:
    def __init__(self, lineno=None, token_type=None, lexeme=None):
        self.lineno = lineno
        self.token_type = token_type
        self.lexeme = lexeme

letters = "qwertyuiopasdfghjklmnbvcxzQWERTYUIOPLKJHGFDSAZXCVBNM"
digits = "0123456789"
symbol = ";:,[](){}+-*=</"
whitespace = "\n\r\t\v\f "
all_valid = letters + digits + symbol + whitespace
keywords = ["if", "else", "void", "int", "break", "return", "while"]
all_chars = "".join([chr(i) for i in range(256)])


the_dfa = initialize_states()

the_lexer = Lexer(Utility.read_input_file(), Utility(), the_dfa)

token_line = the_lexer.curr_lineno
token_list = []
symbol_dict = {}
is_new_line = True
for keyword in keywords:
    symbol_dict[keyword] = keyword

