from interpreter import *


print(Parser(Lexer("((define a 1)(display a))")).parse())
