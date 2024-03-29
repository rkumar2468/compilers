##########################################################
## Lexing and Parsing                                   ##
##                                                      ##
## Author : Rajendra Kumar Raghupatruni                 ##
##                                                      ##
## References: PLY Documentation                        ##
## Links: http://www.dabeaz.com/ply/ply.html#ply_nn4    ##
##                                                      ##
## Python Version: 2.7                                  ##
##########################################################

import ply.lex as lex
import ply.yacc as yacc

# List of tokens #
tokens = [
    'NUMBER',
    'PLUS',
    'MINUS',
    # 'UMINUS',
    'NOT',
    'EQL',
    'DBLEQL',
    'NOTEQL',
    'LT',
    'LE',
    'GT',
    'GE',
    'BINAND',
    'BINOR',
    'MOD',
    'LBRACE',
    'RBRACE',
    'SEMICOLON',
    'TIMES',
    'DIVIDE',
    'LPAREN',
    'RPAREN',
    'VAR'
    ]

## Reserved Keywords ##
reserved = {
    'if' : 'IF',
    'then' : 'THEN',
    'else' : 'ELSE',
    'while' : 'WHILE',
    'do' : 'DO',
    'print' : 'PRINT',
    'input' : 'INPUT'
}

tokens = tokens + reserved.values()
# print tokens

# Regular expression rules for simple tokens #
t_PLUS    	=  r'\+'
t_MINUS    	=  r'-'
t_NOT    	=  r'!'
t_EQL    	=  r'='
t_DBLEQL	=  r'=='
t_NOTEQL	=  r'!='
t_LT    	=  r'<'
t_LE    	=  r'<='
t_GT    	=  r'>'
t_GE    	=  r'>='
t_BINAND    =  r'&&'
t_BINOR    	=  r'\|\|'
t_MOD    	=  r'%'
t_LBRACE    =  r'\{'
t_RBRACE    =  r'\}'
t_SEMICOLON	=  r';'
t_TIMES    	=  r'\*'
t_DIVIDE    =  r'/'
t_LPAREN    =  r'\('
t_RPAREN    =  r'\)'

def t_VAR(t):
    r'[a-zA-Z][a-zA-Z0-9]*'
    ## If lookup fails, it returns the default Var type and value ##
    t.type = reserved.get(t.value, 'VAR')
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Incrementing line number based on the number of \n seen sofar #
def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Ignoring TABS #
t_ignore = ' \t'

def t_COMMENT(t):
    ## Currently supporting only JAVA Style Single Line Comments ##
    ## .* = Zero or more Non New Line characters ##
    r'\/\/.*'
    pass

## Error Handling ##
def t_error(t):
    print "Illegal use of token %s at line: %d" %(t.value[0], t.lexer.lineno)
    t.lexer.skip(1)

# Building the Lexer #
lexer = lex.lex()

## Idea is to get the data from the input file and ##
## and tokenize it by passing it to lexer.         ##

## Testing ##
data = 'x + y'
data += '\n'
data += '10 + 11 - 100'

# lexer.input(data)

## Not working ##
# if lexer:
#     for tok in lexer:
#         print tok

## Print the tokens generated sofar ##
# def printTokens(lexer):
#     print "Printing genenerated:-"
#     print "------------------------"
#     while True:
#         tok = lexer.token()
#         if not tok: break
#         print '[Line: %d] %s' %(tok.lineno, tok)