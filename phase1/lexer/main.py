import dfa
import lexer
import utility

the_dfa = dfa.initialize_states()

the_lexer = lexer.Lexer(utility.Utility.read_input_file(), utility.Utility(), the_dfa)

token_line = the_lexer.curr_lineno
token_list = []
symbol_dict = {}
while True:
    token = the_lexer.get_next_token()
    if token.token_type == dfa.T_group.ID or token.token_type == dfa.T_group.KEYWORD:
        # utility.Utility.write_symbol_file(token.lexeme)
        symbol_dict[token.lexeme] = token.lexeme
    token_current_line = the_lexer.curr_lineno
    if token.token_type not in lexer.Panic_states:
        token_list.append(token)
    else:
        utility.Utility.write_lexical_errors(token.lexeme, token.token_type, token_line)
    if token_line != token_current_line:
        utility.Utility.write_tokens(token_list, token_line)
        token_line = token_current_line
    if the_lexer.is_eof:
        break
for symbol in symbol_dict.keys():
    utility.Utility.write_symbol_file(symbol_dict[symbol])

    
    
