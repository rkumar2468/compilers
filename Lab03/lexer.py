import ply.lex as lex

# Class Lexer:
	# List of token names, is always required
tokens = (
    'NUMBER',
    'PLUS',
    'MINUS',
    'UMINUS',
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
    )

# Regular expression rules for simple tokens
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_UMINUS    = r''
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'




