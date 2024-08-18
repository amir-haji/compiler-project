from alphabet import *
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
    start.add_edge(dest, T_group.FINISH)


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
    s15 = Dfa(15, T_group.KEYWORD_ID, is_panic=True, is_retreat=True)

    add_edges(start, s10, ['/'])
    add_edges(s10, s11, ['/'])
    add_edges(s11, s11, [all_chars.replace('\n', '')])
    add_edges(s11, 12, ['\n'])
    add_eof_edge(s11, s12)
    add_edges(s10, s13, ['*'])
    add_edges(s13, s13, [all_chars.replace('*', '')])
    add_edges(s13, s14, ['*'])
    add_edges(s14, s14, ['*'])
    add_edges(s14, s13, [all_chars.replace('*', '').replace('/', '')])
    add_edges(s14, s12, ['/'])
    add_edges(s10, s15, exclusion(['/', '*']))

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


# initialize_states()






    

