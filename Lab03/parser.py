## Parsing Start    ##
## tokens are already available here ##
import sys
import ply.yacc as yacc
from lexAndParse import tokens

intermediateCode = []

## Classes for each type ##
class Program:
    global intermediateCode
    def __init__(self, stmtSeq):
        self.stmtSeq = stmtSeq
        self.type = 'pgm'

    def genCode(self):
        # print 'Program'
        if self.stmtSeq:
            self.stmtSeq.genCode()

class Statements:
    global intermediateCode
    def __init__(self, stmt, stmtSeq=''):
        self.stmt = stmt
        self.stmtSeq = stmtSeq
        self.type = 'stmtseq'

    def genCode(self):
        if self.stmt:
            self.stmt.genCode()
        if self.stmtSeq:
            self.stmtSeq.genCode()

class Statement:
    global intermediateCode
    def __init__(self, stmt):
        self.stmt = stmt
        self.type = 'stmt'

    def genCode(self):
        if self.stmt:
            self.stmt.genCode()

class Assignment:
    global intermediateCode
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        self.type = 'assign'

    def genCode(self):
        ## Actual Intermediate Code Generation ##
        global intermediateCode
        ret = ''
        # rhs_code =
        if self.rhs.type == 'input':
            intermediateCode.append(self.lhs.genCode())
            intermediateCode.append('=')
            intermediateCode.append('input')
            intermediateCode.append('(')
            intermediateCode.append(')')
            intermediateCode.append(';')
        else:
            if self.rhs.exp.type == 'variable' or self.rhs.exp.type == 'num':
                intermediateCode.append(self.lhs.genCode())
                intermediateCode.append('=')
                intermediateCode.append(self.rhs.genCode())
                intermediateCode.append(';')
            else:
                intermediateCode.append(self.lhs.genCode())
                intermediateCode.append('=')
                self.rhs.genCode()
                intermediateCode.append(';')

class Print:
    global intermediateCode
    def __init__(self, exp):
        self.exp = exp
        self.type = 'print'

    def genCode(self):
        global intermediateCode
        intermediateCode.append('PRINT_START')
        if self.exp.type == 'variable' or self.exp.type == 'num':
            intermediateCode.append(self.exp.genCode())
        else:
            self.exp.genCode()
        intermediateCode.append('PRINT_END')
        # intermediateCode.append(';')

class Block:
    global intermediateCode
    def __init__(self, stmtSeq):
        self.stmtseq = stmtSeq
        self.type = 'block'

    def genCode(self):
        # print "Block Gen Code."
        self.stmtseq.genCode()

class Input:
    def __init__(self):
        self.type = 'input'

    def genCode(self):
        # print "Input Gen Code."
        return 'input()'

class IF:
    global intermediateCode
    def __init__(self, exp, stmt):
        self.exp = exp
        self.stmt = stmt
        self.type = 'if'

    # def evaluateExp(self):

    def genCode(self):
        # print "IF Gen Code."
        global intermediateCode
        # ret = ''
        intermediateCode.append('BRANCH LABEL_IF')
        if self.exp.type == 'variable' or self.exp.type == 'num':
            intermediateCode.append(self.exp.genCode())
            intermediateCode.append(';')
        else:
            self.exp.genCode()
            intermediateCode.append(';')

        # self.exp.genCode() ## x < 10
        self.stmt.genCode()
        intermediateCode.append('BRANCH LABEL_IF_END')
        # intermediateCode.append(ret)

class IFELSE:
    global intermediateCode
    def __init__(self, exp, stmt1, stmt2):
        self.exp = exp
        self.stmt1 = stmt1
        self.stmt2 = stmt2
        self.type = 'ifelse'

    def genCode(self):
        global intermediateCode
        intermediateCode.append('BRANCH LABEL_IF_ELSE')
        if self.exp.type == 'variable' or self.exp.type == 'num':
            intermediateCode.append(self.exp.genCode())
            intermediateCode.append(';')
        else:
            self.exp.genCode()
            intermediateCode.append(';')
        # self.exp.genCode() ## x < 10
        self.stmt1.genCode()
        intermediateCode.append('BRANCH LABEL_ELSE')
        intermediateCode.append(';')
        self.stmt2.genCode()
        intermediateCode.append('BRANCH LABEL_IF_ELSE_END')

class WHILE:
    global intermediateCode
    def __init__(self, exp, stmt):
        self.exp = exp
        self.stmt = stmt
        self.type = 'while'

    def genCode(self):
        # print "While Gen Code."
        global intermediateCode
        intermediateCode.append('BRANCH LABEL_WHILE')
        if self.exp.type == 'variable' or self.exp.type == 'num':
            intermediateCode.append(self.exp.genCode())
            intermediateCode.append(';')
        else:
            self.exp.genCode()
            intermediateCode.append(';')
        # self.exp.genCode() ## x < 10
        self.stmt.genCode()
        intermediateCode.append('BRANCH LABEL_WHILE_END')
        intermediateCode.append(';')

class RHS:
    global intermediateCode
    def __init__(self, exp):
        self.exp = exp
        self.type = 'rhs'

    def genCode(self):
        return self.exp.genCode()

class Expression:
    global intermediateCode
    def __init__(self, exp):
        self.exp = exp
        self.type = 'ae'

    def genCode(self):
        return self.exp.genCode()

class Number:
    global intermediateCode
    def __init__(self, val):
        self.value = val
        self.type = 'num'

    def genCode(self):
        # print "Num Gen Code."
        return str(self.value)

class Unary_Ops:
    global intermediateCode
    def __init__(self, operator, operand):
        self.op = operator
        self.operand = operand
        self.type = 'uops'

    def genCode(self):
        global intermediateCode
        # print "Uops Gen Code."
        ret = 'UNARY '
        ret += self.op
        ret += self.operand.genCode()
        intermediateCode.append(ret)

class Bin_Ops:
    global intermediateCode
    def __init__(self, left, operator, right):
        self.type = 'binop'
        self.left = left
        self.right = right
        self.op = operator

    def genCode(self):
        # print "Bin Ops Gen Code."
        global intermediateCode
        intermediateCode.append('BINARY '+self.op)
        if self.left.type == 'variable' or self.left.type == 'num':
            intermediateCode.append(self.left.genCode())
        else:
            self.left.genCode()
        # ret += self.op
        if self.right.type == 'variable' or self.right.type == 'num':
            intermediateCode.append(self.right.genCode())
        else:
            self.right.genCode()

class Names:
    def __init__(self, var):
        self.var = var
        self.type = 'variable'

    def genCode(self):
        return self.var

## Tracking variables - for static semantic check ##
names = {}

## Precedence and Associativity Rules ##
precedence =(
                ('left','BINOR'),
                ('left','BINAND'),
                ('left','DBLEQL', 'NOTEQL','LT', 'LE', 'GT', 'GE'),
                ('left','PLUS','MINUS'),
                ('left','TIMES','DIVIDE', 'MOD'),
                ('right', 'NOT'),
                ('right','UMINUS')
            )

def p_start(p):
    'pgm : stmtseq'
    p[0] = Program(p[1])

def p_stmtseq(p):
    '''stmtseq : stmt stmtseq
               | stmt'''
    # print len(p)
    if len(p) == 3:
        p[0] = Statements(p[1], p[2])
    else:
        p[0] = Statements(p[1])

def p_stmt(p):
    '''stmt : assign
            | print
            | block
            | if
            | while'''
    p[0] = Statement(p[1])

def p_if(p):
    '''if : IF expression THEN stmt ELSE stmt
          | IF expression THEN stmt'''
    length = len(p)
    if length == 7:
        p[0] = IFELSE(p[2], p[4], p[6])
    elif length == 5:
        p[0] = IF(p[2], p[4])

def p_while(p):
    'while : WHILE expression DO stmt'
    p[0] = WHILE(p[2], p[4])

def p_assign(p):
    'assign : VAR EQL rhs SEMICOLON'
    # pass
    # p[0] = Assignment(p[1], p[3])
    names[p[1]] = p[3]
    p[0] = Assignment(Names(p[1]), p[3])
    # p[0] = '(' + str(p[1]) + '=(' + str(p[3]) + '))'

def p_rhs(p):
    '''rhs : INPUT LPAREN RPAREN
           | expression'''
    if p[1] == 'input':
        print  p[0], "  ", p[1]
        p[0] = Input()
        # p[0] = '(input())'
    else:
        # print len(p)
        p[0] = Expression(p[1])

def p_print(p):
    'print : PRINT LPAREN expression RPAREN SEMICOLON'
    p[0] = Print(p[3])
    # p[0] = '(print(' + str(p[2]) + '))'

def p_block(p):
    'block : LBRACE stmtseq RBRACE'
    p[0] = Block(p[2])

## Expressions Parsing ##

## This is the only way to define UMINUS ##
def p_expression_uminus(p):
    'expression  : MINUS expression %prec UMINUS'
    p[0] = Unary_Ops(p[1], Expression(p[2]))

def p_expression_unary(p):
    'expression : NOT expression'
    p[0] = Unary_Ops(p[1], Expression(p[2]))

def p_expression_paren(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]

## Function Name: p_<Non-Terminal-Symbol>_<Type> ##
## Non Terminal Symbol: expression (can use ae)  ##
## Type: binop                                   ##
def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression MOD expression
                  | expression BINOR expression
                  | expression BINAND expression
                  | expression DBLEQL expression
                  | expression NOTEQL expression
                  | expression LT expression
                  | expression LE expression
                  | expression GT expression
                  | expression GE expression'''
    p[0] = Bin_Ops(p[1], p[2], p[3])
    # p[0] = '(' + str(p[1]) +  str(p[2]) + str(p[3]) + ')'

def p_number(p):
    'expression : NUMBER'
    p[0] = Number(p[1])
    # p[0] = p[1]

def p_names(p):
    'expression : VAR'
    try:
        p[0] = names[p[1]]
        p[0] = Names(p[1])
    except LookupError:
        print("Error: Undefined variable - '%s' at line: %s" % (p[1], p.lexer.lineno))
        # p[0] = 0
        ## Static Semantic Check ##
        ## Exitting on the first error ##
        sys.exit(0)
        ## Can pass if we wish to not to worry about the syntax errors ##
        # pass

## Syntax errors ##
def p_error(p):
    print "Syntax error due to token - '%s' at line: %d " %(p.value, p.lineno)
    sys.exit(0)

def run(data):
    global intermediateCode
    parser = yacc.yacc()
    result = parser.parse(data)
    if result:
        print "Syntax Check Success.!"
    else:
        print "Syntax Check Failed.!\nExitting.!"
        sys.exit(-1)

    result.genCode()
    # print "Intermediate Code: ", intermediateCode