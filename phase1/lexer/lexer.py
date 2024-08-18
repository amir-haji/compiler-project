from dfa import *
from alphabet import *
from enum import Enum
from compiler_token import *


class Panic_states(Enum):
    PANIC_INVALID_INPUT = 'PANIC_INVALID_INPUT'
    PANIC_INVALID_NUMBER = 'PANIC_INVALID_NUMBER'
    PANIC_UNCLOSED_COMMENT = 'PANIC_UNCLOSED_COMMENT'
    PANIC_UNMATCHED_COMMENT = 'PANIC_UNMATCHED_COMMENT'


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
        current_state = self.dfa.states[0]
        lexeme = ""
        start_line = self.curr_lineno
        is_eof_step = False
        while True:
            character = self.util.get_next_char(self.content)
            if character == 'آ':
                try:
                    # current_state = current_state.move_state("FINISH")
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
        if current_state.is_panic or not current_state.is_terminal:
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
