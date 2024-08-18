letters = "qwertyuiopasdfghjklmnbvcxzQWERTYUIOPLKJHGFDSAZXCVBNM"
digits = "0123456789"
symbol = ";:,[](){}+-*=<"
whitespace = "\n\r\t\v\f "
slash = "/"
all_valid = letters + digits + symbol + whitespace + slash
keywords = ["if", "else", "void", "int", "repeat", "break", "until", "return", "endif"]
all_chars = "".join([chr(i) for i in range(256)])