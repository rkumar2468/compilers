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
        self.exp.genCode()

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
        self.exp.genCode()
        ## Resultant is always in $t8 ##
        intermediateCode.append('## Adding New Line ##')
        intermediateCode.append('la $a0, str4')
        intermediateCode.append('li $v0, 4')
        intermediateCode.append('syscall')
        intermediateCode.append('## Printing Integer ##')
        intermediateCode.append('ori $a0, $t8, 0')
        intermediateCode.append('li $v0, 1')
        intermediateCode.append('syscall')
        intermediateCode.append('## End Of Printing Integer ##')
        intermediateCode.append('PRINT_END')

class Block:
    global intermediateCode
    def __init__(self, declseq, stmtSeq):
        self.declseq = declseq
        self.stmtseq = stmtSeq
        self.type = 'block'

    def genCode(self):
        # print "Block Gen Code."
        intermediateCode.append('BLOCK_START')
        # print intermediateCode
        # if not self.stmtseq and not self.declseq:
        #     print 'No Valid statements found in the block. Exitting. \nError.!'
        #     sys.exit(-1)
        if self.declseq:
            self.declseq.genCode()
        if self.stmtseq:
            self.stmtseq.genCode()
        intermediateCode.append('BLOCK_END')
        intermediateCode.append(';')

class Input:
    global intermediateCode
    def __init__(self):
        self.type = 'input'

    def genCode(self):
        intermediateCode.append('## Reading input from stdin ##')
        intermediateCode.append('li $v0, 5')
        intermediateCode.append('syscall')
        intermediateCode.append('ori $t8, $v0, 0')
        intermediateCode.append('## End of input ##')

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
        if self.lbrac and self.rbrac and self.exp:
            self.exp.genCode()
            intermediateCode.append('mult $t8, 4')
            intermediateCode.append('mflo $t9')
            ret = self.id.genCode()
            intermediateCode.append('add $t8, variable_%s, $t9' %(ret))
        else:
            ret = self.id.genCode()
        return ret

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

class SE:
    global intermediateCode
    def __init__(self, lhs, op='', exp=''):
        self.lhs = lhs
        self.exp = exp
        self.op = op
        self.type = 'se'

    def genCode(self):
        if self.op:
            self.exp.genCode()
            ## Result of RHS will be in $t8 ##
            ## Perform the operations ##
            ## Handling '=' ##
            if self.op == '=':
                if self.lhs.type == 'variable':
                    intermediateCode.append('ori variable_%s, $t8, 0' %(self.lhs.var))
                else:
                    ## Array ##
                    intermediateCode.append('ori $a0, $t8, 0')
                    self.lhs.genCode()
                    ## Address to store the value will be in $t8 ##
                    intermediateCode.append('## Storing Register Values to Memory ##')
                    intermediateCode.append('sw $a0, 0($t8)')
        else:
            ## ++, -- will be handled here ##
            ret = self.lhs.genCode()

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
        ## Base address will be in $t8 ##
        ## Assuming everything is integer ##
        self.dimexpr.genCode()
        ## Array Size is in $t8 ##
        intermediateCode.append('ori $a0, $t8, 0')
        intermediateCode.append('## Allocating heap using sbrk system call ##')
        intermediateCode.append('li $v0, 9')
        intermediateCode.append('syscall')
        intermediateCode.append('## End of sbrk system call ##')
        intermediateCode.append('ori $t8, $v0, 0')

## Return Values ##
class Number:
    global intermediateCode
    def __init__(self, val):
        self.value = val
        self.type = 'num'

    def genCode(self):
        code = 'li $t8, %s' %(self.value)
        intermediateCode.append(code)
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
        intermediateCode.append('UNARY START')
        ret = self.operand.genCode()

        if self.post == 0:
            ## Pre Operation ++i ##
            # intermediateCode.append('ori $t9, $t8, 0')
            if self.op == '++':
                intermediateCode.append('addi $t9, $t8, 1')
                intermediateCode.append('ori $t8, $t9, 0')
                if self.operand.type == 'variable' or self.operand.type == 'lhs':
                    intermediateCode.append('ori variable_%s, $t9, 0' %(ret))
            elif self.op == '--':
                intermediateCode.append('li $t9, 1')
                intermediateCode.append('sub $t9, $t8, $t9')
                intermediateCode.append('ori $t8, $t9, 0')
                if self.operand.type == 'variable' or self.operand.type == 'lhs':
                    intermediateCode.append('ori variable_%s, $t9, 0' %(ret))
            elif self.op == '-':
                intermediateCode.append('sub $t9, $zero, $t8')
                intermediateCode.append('ori $t8, $t9, 0')
            elif self.op == '!':
                intermediateCode.append('seq $t9, $t8, $zero')
                intermediateCode.append('ori $t8, $t9, 0')
        else:
            ## Post Operation i++ ##
            # intermediateCode.append('ori $t9, $t8, 0')
            if self.op == '++':
                intermediateCode.append('addi $t9, $t8, 1')
                if self.operand.type == 'variable' or self.operand.type == 'lhs':
                    intermediateCode.append('ori variable_%s, $t9, 0' %ret)
            elif self.op == '--':
                intermediateCode.append('li $t9, 1')
                intermediateCode.append('sub $t9, $t8, $t9')
                if self.operand.type == 'variable' or self.operand.type == 'lhs':
                    intermediateCode.append('ori variable_%s, $t9, 0' %ret)
            elif self.op == '-':
                intermediateCode.append('sub $t9, $zero, $t8')
                intermediateCode.append('ori $t8, $t9, 0')
            elif self.op == '!':
                intermediateCode.append('seq $t9, $t8, $zero')
                intermediateCode.append('ori $t8, $t9, 0')

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
        self.left.genCode()
        if self.op == '+':
            intermediateCode.append('ori $t9, $t8, 0')
            self.right.genCode()
            intermediateCode.append('add $v0, $t9, $t8')
            intermediateCode.append('ori $t8, $v0, 0')
        elif self.op == '-':
            intermediateCode.append('ori $t9, $t8, 0')
            self.right.genCode()
            intermediateCode.append('sub $v0, $t9, $t8')
            intermediateCode.append('ori $t8, $v0, 0')
        elif self.op == '*':
            intermediateCode.append('ori $v0, $t8, 0')
            self.right.genCode()
            intermediateCode.append('mult $t8, $v0')
            intermediateCode.append('mflo $t8')
        elif self.op == '/':
            intermediateCode.append('ori $v0, $t8, 0')
            self.right.genCode()
            intermediateCode.append('div $t8, $v0')
            intermediateCode.append('mflo $t8')
        elif self.op == '%':
            intermediateCode.append('ori $v0, $t8, 0')
            self.right.genCode()
            intermediateCode.append('div $t8, $v0')
            intermediateCode.append('mfhi $t8')
        elif self.op == '||':
            # sne $t9, $t8, $zero; bgez $t9, LABEL
            intermediateCode.append('sne $t9, $t8, $zero')
            intermediateCode.append('bgez $t9, __LABEL__')
            ## Should Peek ##
            self.right.genCode()
            intermediateCode.append('sne $t9, $t8, $zero')
            intermediateCode.append('__POP__LABEL__')
            intermediateCode.append('ori $t8, $t9, 0')
        elif self.op == '&&':
            intermediateCode.append('sne $t9, $t8, $zero')
            intermediateCode.append('beq $t9, $zero, __LABEL__')
            ## Should Peek ##
            self.right.genCode()
            intermediateCode.append('sne $t9, $t8, $zero')
            intermediateCode.append('__POP__LABEL__')
            intermediateCode.append('ori $t8, $t9, 0')
        elif self.op == '==':
            intermediateCode.append('ori $t9, $t8, 0')
            self.right.genCode()
            intermediateCode.append('seq $v0, $t9, $t8')
            intermediateCode.append('ori $t8, $v0, 0')
        elif self.op == '!=':
            intermediateCode.append('ori $t9, $t8, 0')
            self.right.genCode()
            intermediateCode.append('sne $v0, $t9, $t8')
            intermediateCode.append('ori $t8, $v0, 0')
        elif self.op == '<':
            intermediateCode.append('ori $t9, $t8, 0')
            self.right.genCode()
            intermediateCode.append('slt $v0, $t9, $t8')
            intermediateCode.append('ori $t8, $v0, 0')
        elif self.op == '<=':
            intermediateCode.append('ori $t9, $t8, 0')
            self.right.genCode()
            intermediateCode.append('sle $v0, $t9, $t8')
            intermediateCode.append('ori $t8, $v0, 0')
        elif self.op == '>':
            intermediateCode.append('ori $t9, $t8, 0')
            self.right.genCode()
            intermediateCode.append('sgt $v0, $t9, $t8')
            intermediateCode.append('ori $t8, $v0, 0')
        elif self.op == '>=':
            intermediateCode.append('ori $t9, $t8, 0')
            self.right.genCode()
            intermediateCode.append('sge $v0, $t9, $t8')
            intermediateCode.append('ori $t8, $v0, 0')

## Return Values ##
class Names:
    global intermediateCode
    def __init__(self, var):
        self.var = var
        self.type = 'variable'

    def genCode(self):
        code = 'ori $t8, variable_%s, 0' %(self.var)
        intermediateCode.append(code)
        return self.var

## Control Structures ##
class IF:
    global intermediateCode
    def __init__(self, exp, stmt):
        self.exp = exp
        self.stmt = stmt
        self.type = 'if'

    def genCode(self):
        intermediateCode.append('BRANCH LABEL_IF')
        self.exp.genCode()
        intermediateCode.append('beq $t8, $zero, __IF_LABEL__')
        ## Should do peek here ##
        self.stmt.genCode()
        intermediateCode.append('BRANCH LABEL_IF_END')
        ## Should do pop here ##
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
        self.exp.genCode()
        intermediateCode.append('beq $t8, $zero, __IF_LABEL__')
        ## Should do peek-1 here ##
        self.stmt1.genCode()
        intermediateCode.append('b __IF_LABEL__')
        ## Should do peek-2 here ##
        intermediateCode.append('BRANCH LABEL_ELSE')
        ## Should do pop-1 here ##
        intermediateCode.append(';')
        self.stmt2.genCode()
        intermediateCode.append('BRANCH LABEL_IF_ELSE_END')
        ## Should do pop-2 here ##
        intermediateCode.append(';')

class WHILE:
    global intermediateCode
    def __init__(self, exp, stmt):
        self.exp = exp
        self.stmt = stmt
        self.type = 'while'

    def genCode(self):
        intermediateCode.append('BRANCH LABEL_WHILE')
        intermediateCode.append('__WHILE_LABEL_START__')
        self.exp.genCode()
        intermediateCode.append('beq $t8, $zero, __WHILE_LABEL__')
        self.stmt.genCode()
        intermediateCode.append('b __WHILE_LABEL_START__')
        ## POP-1 While Label ##
        intermediateCode.append('BRANCH LABEL_WHILE_END')
        ## POP-2 While Label ##
        intermediateCode.append(';')

## Homework 04 Updates ##
class FOR:
    global intermediateCode
    def __init__(self, arg1, arg2, arg3, arg4):
        self.seopt1 = arg1
        self.aeopt = arg2
        self.seopt2 = arg3
        self.stmt = arg4

    def genCode(self):
        intermediateCode.append('BRANCH LABEL_FOR')
        if self.seopt1:
            self.seopt1.genCode()
        intermediateCode.append('__FOR_LABEL_START__')
        if self.aeopt:
            self.aeopt.genCode()
            intermediateCode.append('beq $t8, $zero, __FOR_LABEL__')
        self.stmt.genCode()
        if self.seopt2:
            self.seopt2.genCode()
        intermediateCode.append('b __FOR_LABEL_START__')
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
        intermediateCode.append('__WHILE_LABEL_START__')
        self.stmt.genCode()
        self.exp.genCode()
        intermediateCode.append('beq $t8, $zero, __WHILE_LABEL__')
        intermediateCode.append('b __WHILE_LABEL_START__')
        ## POP-1 While Label ##
        intermediateCode.append('BRANCH LABEL_DO_WHILE_END')
        ## POP-2 While Label ##
        intermediateCode.append(';')

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
    if p[1] == '++' or p[1] == '--':
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
        print "Parsing Completed.!"
    else:
        print "Syntax Check Failed.!\nExitting.!"
        sys.exit(-1)

    result.genCode()

