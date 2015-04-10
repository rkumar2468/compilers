## Parsing Start    ##
## tokens are already available here ##
import sys
import ply.yacc as yacc
from lexAndParse import tokens

intermediateCode = []

## Classes for each type ##
## Pgm ##
class Program:
    global intermediateCode
    def __init__(self, DeclSeq, stmtSeq):
        self.stmtSeq = stmtSeq
        self.declseq = DeclSeq
        self.type = 'pgm'

    def genCode(self):
        # print 'Program'
        # if not self.declseq:
        #     print "Error in the input proto file, no declaration statements found.!"
        #     sys.exit(-1)
        intermediateCode.append('BLOCK_START')
        if self.declseq:
            self.declseq.genCode()
        if self.stmtSeq:
            self.stmtSeq.genCode()
        intermediateCode.append('BLOCK_END')

class DECLSEQ:
    def __init__(self, decl='', declSeq=''):
        self.decl = decl
        self.declseq = declSeq

    def genCode(self):
        if self.decl:
            self.decl.genCode()
            if self.declseq:
                self.declseq.genCode()

class DECL:
    global intermediateCode
    def __init__(self, type, varlist):
        self.type = type
        self.varlist = varlist

    def genCode(self):
        global intermediateCode
        intermediateCode.append('TYPE '+self.type.genCode())
        self.varlist.genCode()
        intermediateCode.append(';')

class TYPE:
    def __init__(self, type):
        self.type = type

    def genCode(self):
        return self.type

class VARLIST:
    global intermediateCode
    def __init__(self, var, comma='', varlist=''):
        self.var = var
        self.varlist  = varlist
        self.comma = comma

    def genCode(self):
        self.var.genCode()
        if self.comma:
            intermediateCode.append(self.comma)
        if self.varlist:
            self.varlist.genCode()
        # return ret

class VAR:
    global intermediateCode
    def __init__(self, var, dimstar=''):
        self.var = var
        self.dimstar  = dimstar

    def genCode(self):
        intermediateCode.append(self.var)
        if self.dimstar:
            self.dimstar.genCode()
        # return ret

class DIMSTAR:
    global intermediateCode
    def __init__(self, lbrac='', rbrac='', dimstar=''):
        self.lbrac = lbrac
        self.rbrac = rbrac
        self.dimstar = dimstar

    def genCode(self):
        global intermediateCode
        if self.lbrac and self.rbrac:
            intermediateCode.append(self.lbrac)
            intermediateCode.append(self.rbrac)
        if self.dimstar:
            self.dimstar.genCode()

class DIMEXPR:
    global intermediateCode
    def __init__(self, lbrac, exp, rbrac):
        self.lbrac = lbrac
        self.rbrac = rbrac
        self.exp = exp

    def genCode(self):
        global intermediateCode
        intermediateCode.append(self.lbrac)
        ret = self.exp.genCode()
        if ret != None:
            intermediateCode.append(ret)
        intermediateCode.append(self.rbrac)

## StmtSeq ##
class Statements:
    global intermediateCode
    def __init__(self, stmt='', stmtSeq=''):
        self.stmt = stmt
        self.stmtSeq = stmtSeq
        self.type = 'stmtseq'

    def genCode(self):
        if self.stmt:
            self.stmt.genCode()
        if self.stmtSeq:
            self.stmtSeq.genCode()

## Stmt ##
class Statement:
    global intermediateCode
    def __init__(self, stmt):
        self.stmt = stmt
        self.type = 'stmt'

    def genCode(self):
        if self.stmt:
            self.stmt.genCode()
            intermediateCode.append(';')

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
        # global intermediateCode
        intermediateCode.append('PRINT_START')
        if (self.exp.type == 'variable' or self.exp.type == 'num')\
                or \
            (self.exp.type == 'ae' and (self.exp.exp.type == 'variable' or self.exp.exp.type == 'num')):
            intermediateCode.append(self.exp.genCode())
        else:
            ret = self.exp.genCode()
            if ret != None:
                intermediateCode.append(ret)
        intermediateCode.append('PRINT_END')
        intermediateCode.append(';')

class Block:
    global intermediateCode
    def __init__(self, declseq, stmtSeq):
        self.declseq = declseq
        self.stmtseq = stmtSeq
        self.type = 'block'

    def genCode(self):
        # print "Block Gen Code."
        intermediateCode.append('BLOCK_START')
        if not self.stmtseq or not self.declseq:
            sys.exit(-1)
        self.declseq.genCode()
        self.stmtseq.genCode()
        intermediateCode.append('BLOCK_END')
        intermediateCode.append(';')

class Input:
    global intermediateCode
    def __init__(self):
        self.type = 'input'

    def genCode(self):
        # print "Input Gen Code."
        intermediateCode.append('input')
        intermediateCode.append('(')
        intermediateCode.append(')')

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
        if (self.exp.type == 'variable' or self.exp.type == 'num') \
                or\
            (self.exp.type == 'ae' and (self.exp.exp.type == 'variable' or self.exp.exp.type == 'num')):
            intermediateCode.append(self.exp.genCode())
            intermediateCode.append(';')
        else:
            self.exp.genCode()
            intermediateCode.append(';')

        # self.exp.genCode() ## x < 10
        self.stmt.genCode()
        intermediateCode.append('BRANCH LABEL_IF_END')
        intermediateCode.append(';')

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
        if (self.exp.type == 'variable' or self.exp.type == 'num') \
                or \
                (self.exp.type == 'ae' and (self.exp.exp.type == 'variable' or self.exp.exp.type == 'num')):
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
        intermediateCode.append(';')

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
        if (self.exp.type == 'variable' or self.exp.type == 'num')\
                or \
            (self.exp.type == 'ae' and (self.exp.exp.type == 'variable' or self.exp.exp.type == 'num')):
            intermediateCode.append(self.exp.genCode())
            intermediateCode.append(';')
        else:
            self.exp.genCode()
            intermediateCode.append(';')
        # self.exp.genCode() ## x < 10
        self.stmt.genCode()
        intermediateCode.append('BRANCH LABEL_WHILE_END')
        intermediateCode.append(';')

## Return Values ##
class LHS:
    global intermediateCode
    def __init__(self, id, lbrac='', exp='', rbrac=''):
        self.id = id
        self.lbrac = lbrac
        self.rbrac = rbrac
        self.exp = exp
        self.type = 'lhs'

    def genCode(self):
        intermediateCode.append(self.id.genCode())
        if self.lbrac and self.rbrac and self.exp:
            intermediateCode.append('[')
            intermediateCode.append(self.exp.genCode())
            intermediateCode.append(']')

class SEOPT:
    def __init__(self, se=''):
        self.se = se

    def genCode(self):
        if self.se:
            self.se.genCode()

class AEOPT:
    global intermediateCode
    def __init__(self, exp=''):
        self.exp = exp

    def genCode(self):
        if self.exp:
            self.exp.genCode()

## Raj - Should handle pre and post increment/decrement operations -- Done ##
class SE:
    global intermediateCode
    def __init__(self, lhs, op='', exp=''):
        self.lhs = lhs
        self.exp = exp
        self.op = op
        self.type = 'se'

    def genCode(self):
        ret = self.lhs.genCode()
        if ret != None:
            intermediateCode.append(ret)
        if self.op:
            intermediateCode.append(self.op)
        if self.exp:
            # print self.exp,
            if (self.exp.type == 'variable' or self.exp.type == 'num')\
                or \
            (self.exp.type == 'ae' and (self.exp.exp.type == 'variable' or self.exp.exp.type == 'num')):
                # if self.pre == 1:
                intermediateCode.append(self.exp.genCode())
            else:
                ret = self.exp.genCode()
                if ret != None:
                    intermediateCode.append(ret)
        # intermediateCode.append(';')

## Return Values ##
class Expression:
    global intermediateCode
    def __init__(self, exp):
        self.exp = exp
        self.type = 'ae'

    def genCode(self):
        if self.exp == 'true':
            return 'true'
        elif self.exp == 'false':
            return 'false'
        return self.exp.genCode()

class ARRAY:
    global intermediateCode
    def __init__(self, new, type, dimexpr, dimstar):
        self.keyword = new
        self.TYPE = type
        self.dimexpr = dimexpr
        self.dimstar = dimstar
        self.type = 'array'

    def genCode(self):
        # return self.exp.genCode()
        # print 'Arrays: To be implemented.!'
        intermediateCode.append(self.keyword)
        intermediateCode.append(self.TYPE.genCode())
        self.dimexpr.genCode()
        if self.dimstar:
            self.dimstar.genCode()

## Return Values ##
class Number:
    global intermediateCode
    def __init__(self, val):
        self.value = val
        self.type = 'num'

    def genCode(self):
        # intermediateCode.append(self.value)
        return str(self.value)

## No Return values ##
class Unary_Ops:
    global intermediateCode
    def __init__(self, operator, operand, post=0):
        self.op = operator
        self.operand = operand
        self.type = 'uops'
        self.post= post

    def genCode(self):
        global intermediateCode
        # print "Uops Gen Code."
        # ret = ''
        intermediateCode.append('UNARY START')
        if self.post == 0:
            intermediateCode.append(self.op)
            # if self.operand.type and self.operand.type == 'ae':
            #     intermediateCode.append(self.operand.genCode())
            # else:
            if self.operand:
                ret = self.operand.genCode()
            if ret != None:
                intermediateCode.append(ret)
        else:
            # if self.operand.type and self.operand.type == 'ae':
                # self.operand.genCode()
            # else:
            if self.operand:
                ret = self.operand.genCode()
            if ret != None:
                intermediateCode.append(ret)
            intermediateCode.append(self.op)
        intermediateCode.append('UNARY END')

## No Return values ##
class Bin_Ops:
    global intermediateCode
    def __init__(self, left, operator, right):
        self.type = 'binop'
        self.left = left
        self.right = right
        self.op = operator

    def genCode(self):
        global intermediateCode
        intermediateCode.append('BINARY '+self.op)
        if (self.left.type == 'variable' or self.left.type == 'num')\
                or \
            (self.left.type == 'ae' and (self.left.exp.type == 'variable' or self.left.exp.type == 'num')):
            intermediateCode.append(self.left.genCode())
        else:
            self.left.genCode()
        # ret += self.op
        if (self.right.type == 'variable' or self.right.type == 'num')\
                or \
            (self.right.type == 'ae' and (self.right.exp.type == 'variable' or self.right.exp.type == 'num')):
            intermediateCode.append(self.right.genCode())
        else:
            self.right.genCode()

## Return Values ##
class Names:
    global intermediateCode
    def __init__(self, var):
        self.var = var
        self.type = 'variable'

    def genCode(self):
        # intermediateCode.append(self.var)
        return self.var

## Homework 04 Updates ##
class FOR:
    global intermediateCode
    def __init__(self, arg1, arg2, arg3, arg4):
        self.seopt1 = arg1
        self.aeopt = arg2
        self.seopt2 = arg3
        self.stmt = arg4

    def genCode(self):
        # print 'To be implemented.'
        intermediateCode.append('BRANCH LABEL_FOR')
        self.seopt1.genCode()
        intermediateCode.append(';')
        self.aeopt.genCode()
        intermediateCode.append(';')
        # self.seopt2.genCode()
        intermediateCode.append(';')
        self.stmt.genCode()
        intermediateCode.append('BRANCH LABEL_FOR_END')
        intermediateCode.append(';')

class DO_WHILE:
    global intermediateCode
    def __init__(self, stmt, exp):
        self.exp = exp
        self.stmt = stmt
        self.type = 'do_while'

    def genCode(self):
        intermediateCode.append('BRANCH LABEL_DO_WHILE')
        intermediateCode.append(';')
        self.stmt.genCode()
        intermediateCode.append('BRANCH LABEL_DO_WHILE_END')
        if (self.exp.type == 'variable' or self.exp.type == 'num')\
                or \
            (self.exp.type == 'ae' and (self.exp.exp.type == 'variable' or self.exp.exp.type == 'num')):
            intermediateCode.append(self.exp.genCode())
            intermediateCode.append(';')
        else:
            self.exp.genCode()
            intermediateCode.append(';')
        # intermediateCode.append(';')

## Tracking variables - for static semantic check ##
names = {}

## Precedence and Associativity Rules ##
precedence =(
                ('nonassoc', 'ELSE'),
                ('nonassoc', 'THEN'),
                ('nonassoc', 'IF'),
                ('right', 'EQL'),
                ('left','BINOR'),
                ('left','BINAND'),
                ('nonassoc','DBLEQL', 'NOTEQL'),
                ('nonassoc','LT', 'LE', 'GT', 'GE'),
                ('left','PLUS','MINUS'),
                ('left','TIMES','DIVIDE', 'MOD'),
                ('nonassoc','UMINUS', 'NOT')
            )

def p_start(p):
    'pgm : declseq stmtseq'
    p[0] = Program(p[1], p[2])

def p_declseq(p):
    '''declseq : decl declseq
               | '''
    if len(p) == 3:
        p[0] = DECLSEQ(p[1], p[2])
    # else:
    #     p[0] = DECLSEQ()

def p_decl(p):
    'decl : type varlist SEMICOLON'
    if len(p) == 4:
        p[0] = DECL(p[1], p[2])


def p_stmtseq(p):
    '''stmtseq : stmt stmtseq
               | '''
    if len(p) == 3:
        p[0] = Statements(p[1], p[2])
    # else:
    #     p[0] = Statements()

def p_stmt(p):
    '''stmt : SE SEMICOLON
            | print
            | block
            | if
            | while
            | for
            | do_while'''
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

def p_do_while(p):
    'do_while : DO stmt WHILE expression SEMICOLON'
    p[0] = DO_WHILE(p[2], p[4])

def p_for(p):
    'for : FOR LPAREN SEOpt SEMICOLON AEOpt SEMICOLON SEOpt RPAREN stmt'
    p[0] = FOR(p[3], p[5], p[7], p[9])

def p_seopt(p):
    '''SEOpt : SE
            | '''
    if len(p) == 2:
        p[0] = SEOPT(p[1])
    # else:
    #     p[0] = SEOPT()

def p_aeopt(p):
    '''AEOpt : expression
            | '''
    if len(p) == 2:
        p[0] = AEOPT(p[1])
    # else:
    #     p[0] = AEOPT()

def p_type(p):
    '''type : INT
           | BOOL'''
    p[0] = TYPE(p[1])

def p_varlist(p):
    '''varlist : var COMMA varlist
              | var'''
    if len(p) == 4:
        p[0] = VARLIST(p[1], p[2], p[3])
    elif len(p) == 2:
        p[0] = VARLIST(p[1])

def p_var(p):
    'var : ID dimstar'
    p[0] = VAR(p[1], p[2])

def p_se(p):
    '''SE : lhs EQL expression
          | prepost'''
    if len(p) == 4:
        ## = operation ##
        p[0] = SE(p[1], p[2], Expression(p[3]))
    else:
        p[0] = SE(p[1])

def p_unaryPrePost(p):
    '''prepost : lhs PLUSPLUS
               | lhs MINUSMINUS
               | PLUSPLUS lhs
               | MINUSMINUS lhs'''
    if p[1] == '\+\+' or p[1] == '--':
        ## Pre ##
        p[0] = Unary_Ops(p[1], LHS(p[2]), 0)
    else:
        ## Post ##
        p[0] = Unary_Ops(p[2], LHS(p[1]), 1)

def p_lhs(p):
    'lhs : lhs LSQUAREBRACE expression RSQUAREBRACE'
    # names[p[1]] = p[3]
    p[0] = LHS(p[1], p[2], Expression(p[3]), p[4])

def p_expression(p):
    '''expression : lhs
                  | SE
                  | input
                  | TRUE
                  | FALSE
                  | array'''
    p[0] = Expression(p[1])

def p_array(p):
    'array : NEW type dimexpr dimstar'
    p[0] = ARRAY(p[1], p[2], p[3], p[4])

def p_dimexpr(p):
    'dimexpr : LSQUAREBRACE expression RSQUAREBRACE'
    p[0] = DIMEXPR(p[1], Expression(p[2]), p[3])

def p_dimstar(p):
    '''dimstar : LSQUAREBRACE RSQUAREBRACE dimstar
             | '''
    if len(p) > 1:
        if p[3]:
            p[0] = DIMSTAR(p[1], p[2], p[3])
        else:
            p[0] = DIMSTAR(p[1], p[2])
    else:
        p[0] = DIMSTAR()

def p_input(p):
    '''input : INPUT LPAREN RPAREN'''
    p[0] = Input()

def p_print(p):
    'print : PRINT LPAREN expression RPAREN SEMICOLON'
    p[0] = Print(p[3])

def p_block(p):
    'block : LBRACE declseq stmtseq RBRACE'
    p[0] = Block(p[2], p[3])

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

## intconst ##
def p_number(p):
    'expression : NUMBER'
    p[0] = Number(p[1])

## Basic static semantics ##
def p_id(p):
    'lhs : ID'
    try:
        # p[0] = names[p[1]]
        p[0] = Names(p[1])
    except LookupError:
        print("Error: Undefined variable - '%s' at line: %s" % (p[1], p.lexer.lineno))
        sys.exit(0)

## Syntax errors ##
def p_error(p):
    print "Syntax error due to token - '%s' at line: %d " %(p.value, p.lineno)
    sys.exit(0)

def run(data):
    global intermediateCode
    parser = yacc.yacc()
    result = parser.parse(data)
    if result:
        # print "Syntax Check Success.!"
        print "Parsing Completed.!"
    else:
        print "Syntax Check Failed.!\nExitting.!"
        sys.exit(-1)

    result.genCode()
    # print "Intermediate Code: ", intermediateCode

