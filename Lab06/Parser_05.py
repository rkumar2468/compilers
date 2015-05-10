## Parsing Start    ##
## tokens are already available here ##
import sys, copy
import ply.yacc as yacc
from lexAndParse import tokens

intermediateCode = []
tempCode = []
sta_arg = 0
fun_param_dict = {}
fun_param_count = []
blockVar = {}
currBlock = 0
declared = 0
mainFun = 0
otherFun = 0
types = {}
currType = ''
# constantPropagation = {}
loopblock = 0
optBlock = 0
optBlockVar = {}

constPropStack = {}

# For Constant propagation #
def checkIfVarInStackDict(var, stackDict, block):
    if block == 0 and block in stackDict.keys():
        if var in stackDict[block].keys():
            return True
    for i in range(block+1):
        cur = block - i
        try:
            if var in stackDict[cur].keys():
                return True
        except KeyError:
            pass
    return False

def removeEntryFromDict(key, dict):
    try:
        print "Popped: ", dict.pop(key)
    except KeyError:
        pass

# For Constant propagation #
def getLatestValFromStackDict(var, stackDict, block):
    if block == 0 and block in stackDict.keys():
        if var in stackDict[block].keys():
            return stackDict[block][var]
    for i in range(block+1):
        cur = block - i
        try:
            if var in stackDict[cur].keys():
                return stackDict[cur][var]
        except KeyError:
            pass
    # return

def getTypeValue(dict, val):
    for key in dict.keys():
        if val in dict[key]:
            return key

def getTypes(variable, block):
    list = []
    if block in types.keys():
        typeV = getTypeValue(types[block], variable)
        if typeV:
            return typeV
        else:
            for i in range(block):
                try:
                    typeV = getTypeValue(types[block - i - 1], variable)
                except KeyError:
                    continue
                if typeV:
                    return typeV
    else:
        for i in range(block):
            try:
                typeV = getTypeValue(types[block - i - 1], variable)
            except KeyError:
                continue
            if typeV:
                return typeV

def typeChecking(variable, type, block):
    list = []
    if block in types.keys():
        try:
            list = types[block][type]
        except KeyError:
            pass
        if variable in list:
            return True
        else:
            for i in range(block):
                if i in types.keys():
                    try:
                       list = types[block - i - 1][type]
                    except KeyError:
                        continue
                    if variable in list:
                        return True
            return False
    else:
        for i in range(block):
            # if i in types.keys():
            try:
                list = types[block - i - 1][type]
            except KeyError:
                continue
            if variable in list:
                return True
    return False

def removeVarDeclFromDict():
    global blockVar, currBlock
    if currBlock in blockVar.keys():
        blockVar[currBlock] = []

def checkDeclaration(blockVar, currBlock, var):
    for i in range(currBlock+1):
        if i in blockVar.keys():
            if var in blockVar[i]:
                return 1
    return 0

## Utility function to add Types for each variable per block ##
def addToTypesDict(variable, typeVal, blckno):
    dictType = {}
    if blckno in types.keys():
            dictType = types[blckno]
            if typeVal in dictType.keys():
                dictType[typeVal].append(variable)
            else:
                dictType[typeVal] = [variable]
    else:
        dictType[typeVal] = [variable]
        types[currBlock] = dictType

## Classes for each type ##
## Pgm ##
class Program:
    global intermediateCode
    def __init__(self, DeclSeq):
        self.declseq = DeclSeq
        self.type = 'pgm'

    def genCode(self):
        intermediateCode.append('BLOCK_START')
        if self.declseq:
            self.declseq.genCode()
        intermediateCode.append('BLOCK_END')

    def constPropagationOpt(self):
        self.declseq = self.declseq.constPropagationOpt()
        return self

class DECLSEQ:
    def __init__(self, declare='', declSeq=''):
        self.declare = declare
        self.declseq = declSeq

    def genCode(self):
        if self.declare:
            self.declare.genCode()
            if self.declseq:
                self.declseq.genCode()

    def constPropagationOpt(self):
        if self.declare:
            self.declare = self.declare.constPropagationOpt()
            if self.declseq:
                self.declseq = self.declseq.constPropagationOpt()
        return self

class DECLARE:
    def __init__(self, declare):
        ## Can be either Var or Func Declaration ##
        self.declare = declare

    def genCode(self):
        self.declare.genCode()

    def constPropagationOpt(self):
        self.declare = self.declare.constPropagationOpt()
        return self

## Variable Declaration ##
class DECL:
    global intermediateCode
    def __init__(self, type, varlist):
        self.type = type
        self.varlist = varlist

    def genCode(self):
        global intermediateCode, declared, currType
        declared = 1
        currType = self.type.genCode()
        intermediateCode.append('TYPE '+currType)
        self.varlist.genCode()
        currType = ''
        intermediateCode.append(';')
        declared = 0

    def constPropagationOpt(self):
        self.varlist = self.varlist.constPropagationOpt()
        return self

class TYPE:
    def __init__(self, type):
        self.type = type
        # self.TYPEV = type

    def genCode(self):
        if isinstance(self.type, TYPE):
            return self.type.gettype()+'[]'
        else:
            return self.type

    def gettype(self):
        if isinstance(self.type, TYPE):
            return self.type.gettype()+'[]'
        else:
            return self.type

    def constPropagationOpt(self):
        return self

## Function Declaration ##
class FUNDECL:
    global intermediateCode
    def __init__(self, type, id, stmt, formals):
        self.type = type
        self.id = id
        self.stmt = stmt
        self.formals = formals

    def genCode(self):
        global currBlock, mainFun, otherFun, blockVar, fun_param_count, sta_arg
        nargs = 0
        # localDict = {}
        ## Function Handling ##
        ## The Start and End tags are used to separate the functions ##
        ## So that the definitions can be placed anywhere other than within the main function ##
        intermediateCode.append('FUNCTION_BLOCK')
        if currBlock in blockVar.keys():
            blockVar[currBlock].append(self.id.var)
        else:
            blockVar[currBlock] = [self.id.var]
        # print blockVar
        currBlock += 1
        if self.id.var == 'main':
            mainFun = 1
            otherFun = 0
        else:
            mainFun = 0
            otherFun = 1

        intermediateCode.append('%s:' %(self.id.var))
        if self.formals:
            ## Put the variables in some memory locations or stack ##
            nargs = self.formals.genCode()
        sta_arg = 0
        fun_param_count.append([self.id.var, nargs])

        ## Loading the stack pointer ##
        ## The below initialization is not required in function definition ##
        ## This is taken care at the time of calling ##
        # intermediateCode.append('la $s0, stack')

        ## Run the function code ##
        self.stmt.genCode()
        ## Results of all functions should be in $v0 ##
        # intermediateCode.append('ori $v0, $t8, 0')
        # intermediateCode.append('jr $ra')
        intermediateCode.append('FUNCTION_BLOCK_END')
        if self.id.var == 'main':
            mainFun = 0
        else:
            otherFun = 0
        fun_param_count.pop()
        currBlock -= 1

    def constPropagationOpt(self):
        self.stmt = self.stmt.constPropagationOpt()
        self.id = self.id.constPropagationOpt()
        if self.formals:
            self.formals = self.formals.constPropagationOpt()
        return self

class FORMALS:
    def __init__(self, formal=''):
        self.formal = formal
        self.type = 'formal'

    def genCode(self):
        ret =  0
        if self.formal:
            ret = self.formal.genCode()
        return ret

    def constPropagationOpt(self):
        return self

class Formal:
    global intermediateCode
    global sta_arg
    def __init__(self, type, var, formal=''):
        self.type = type
        self.var = var
        self.formal = formal

    def genCode(self):
        global sta_arg, fun_param_dict, currBlock
        name = self.var.var
        if name not in blockVar[0]:
            fun_param_dict[name] = int(sta_arg)*4

        if currBlock in blockVar.keys():
            if name in blockVar[currBlock]:
                print "Error: Variable %s declared more than once." %(name)
                sys.exit(-1)
            blockVar[currBlock].append(name)
        else:
            blockVar[currBlock] = [name]

        addToTypesDict(name, self.type.genCode(), currBlock)

        sta_arg += 1
        if self.formal:
            self.formal.genCode()
        return sta_arg

    def constPropagationOpt(self):
        self.var = self.var.constPropagationOpt()
        return self

class VARLIST:
    global intermediateCode
    def __init__(self, var, comma='', varlist=''):
        self.var = var
        self.varlist  = varlist
        self.comma = comma

    def genCode(self):
        global blockVar, currBlock, types, currType
        name = self.var.genCode()
        addToTypesDict(name, currType, currBlock)
        if currBlock in blockVar.keys():
            if name in blockVar[currBlock]:
                print "Error: Variable %s declared more than once." %(name)
                sys.exit(-1)
            blockVar[currBlock].append(name)
        else:
            blockVar[currBlock] = [name]

        if self.comma:
            intermediateCode.append(self.comma)
        if self.varlist:
            self.varlist.genCode()

    def constPropagationOpt(self):
        self.var = self.var.constPropagationOpt()
        if self.varlist:
            self.varlist = self.varlist.constPropagationOpt()
        return self

## Var is deprecated - Reusing for some other issue ##
class VAR:
    global intermediateCode
    def __init__(self, var):
        self.var = var

    def genCode(self):
        intermediateCode.append(self.var)
        return self.var

    def constPropagationOpt(self):
        return self

class DIMSTAR:
    global intermediateCode
    def __init__(self, lbrac='', rbrac='', dimstar=''):
        self.lbrac = lbrac
        self.rbrac = rbrac
        self.dimstar = dimstar
        self.TYPEV = ''

    def genCode(self):
        global intermediateCode
        if self.lbrac and self.rbrac:
            intermediateCode.append(self.lbrac)
            intermediateCode.append(self.rbrac)
            self.TYPEV = '[]'
        if self.dimstar:
            self.dimstar.genCode()
            self.TYPEV += self.dimstar.gettype()

    def gettype(self):
        if not self.TYPEV:
            self.genCode()
        return self.TYPEV

    def constPropagationOpt(self):
        return self

class DIMEXPR:
    global intermediateCode
    def __init__(self, lbrac, exp, rbrac):
        self.lbrac = lbrac
        self.rbrac = rbrac
        self.exp = exp
        self.TYPEV = '[]'

    def genCode(self):
        self.exp.genCode()

    def gettype(self):
        return self.TYPEV

    def constPropagationOpt(self):
        self.exp = self.exp.constPropagationOpt()
        return self

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

    def constPropagationOpt(self):
        if self.stmt:
            self.stmt = self.stmt.constPropagationOpt()
        if self.stmtSeq:
            self.stmtSeq = self.stmtSeq.constPropagationOpt()
        return self

## VarDecl* ##
class VARDECLSEQ:
    global intermediateCode
    def __init__(self, varDecl='', varDeclSeq=''):
        self.varDecl = varDecl
        self.varDeclSeq = varDeclSeq
        self.type = 'vardeclseq'

    def genCode(self):
        if self.varDecl:
            self.varDecl.genCode()
        if self.varDeclSeq:
            self.varDeclSeq.genCode()

    def constPropagationOpt(self):
        if self.varDecl:
            self.varDecl = self.varDecl.constPropagationOpt()
        if self.varDeclSeq:
            self.varDeclSeq = self.varDeclSeq.constPropagationOpt()
        return self

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

    def constPropagationOpt(self):
        if self.stmt:
            self.stmt = self.stmt.constPropagationOpt()
        return self

class RETURN:
    global intermediateCode
    def __init__(self, exp=''):
        self.exp = exp

    def genCode(self):
        global mainFun
        ## Return Value will always be in $t8
        if self.exp:
            self.exp.genCode()
        else:
            intermediateCode.append('li $t8, 0')
        if mainFun == 0:
            intermediateCode.append('jr $ra')
        else:
            intermediateCode.append('j exit')

    def constPropagationOpt(self):
        if self.exp:
            self.exp = self.exp.constPropagationOpt()
        return self

## Deprecated class ##
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

    def constPropagationOpt(self):
        ## Here is the actual constant propagation starts ##
        return self

class Print:
    global intermediateCode
    def __init__(self, exp):
        self.exp = exp
        self.type = 'print'

    def genCode(self):
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
        if self.exp.gettype() != 'int':
            print "Error: Printing non integer values.!"
            sys.exit(-1)

    def constPropagationOpt(self):
        self.exp = self.exp.constPropagationOpt()
        return self

class Block:
    global intermediateCode
    def __init__(self, declseq, stmtSeq):
        self.declseq = declseq
        self.stmtseq = stmtSeq
        self.type = 'block'

    def genCode(self):
        global currBlock
        intermediateCode.append('BLOCK_START')
        currBlock += 1
        if self.declseq:
            self.declseq.genCode()
        if self.stmtseq:
            self.stmtseq.genCode()
        intermediateCode.append('BLOCK_END')
        intermediateCode.append(';')
        removeVarDeclFromDict()
        currBlock -= 1

    def constPropagationOpt(self):
        global optBlock
        if self.declseq:
            self.declseq = self.declseq.constPropagationOpt()
        if self.stmtseq:
            self.stmtseq = self.stmtseq.constPropagationOpt()
        return self

class Input:
    global intermediateCode
    def __init__(self):
        self.type = 'input'
        self.TYPEV = 'input'

    def genCode(self):
        intermediateCode.append('## Reading input from stdin ##')
        intermediateCode.append('li $v0, 5')
        intermediateCode.append('syscall')
        intermediateCode.append('ori $t8, $v0, 0')
        intermediateCode.append('## End of input ##')

    def gettype(self):
        return self.TYPEV

    def constPropagationOpt(self):
        return self

## Return Values ##
class LHS:
    global intermediateCode
    def __init__(self, id_or_array):
        self.id_or_array = id_or_array
        self.type = 'lhs'
        self.TYPEV = ''

    def genCode(self):
        ret = self.id_or_array.genCode()
        self.TYPEV = self.id_or_array.gettype()
        return ret

    def gettype(self):
        if not self.TYPEV:
            self.TYPEV = self.id_or_array.gettype()
        return self.TYPEV

    def constPropagationOpt(self):
        self.id_or_array = self.id_or_array.constPropagationOpt()
        return self

class ArrayAccess:
    global intermediateCode
    def __init__(self, primary, exp):
        self.primary = primary
        self.exp = exp
        self.type = 'arrayaccess'
        self.TYPEV = ''

    def genCode(self):
        self.primary.genCode()
        ## $t8 = a in case of a[i] ##
        ## $t8 = a in case of a[i][j] ##
        ## The below line doesnt class with $a0 used in SE ##
        ## So its safe to use here ##
        intermediateCode.append('ori $a0, $t8, 0')
        self.exp.genCode()
        if self.exp.gettype() != 'int':
            print "Error: Array index is not an integer.!"
            sys.exit(-1)
        intermediateCode.append('mult $t8, 4')
        intermediateCode.append('mflo $t9')
        intermediateCode.append('add $t8, $a0, $t9')
        # return ret
        self.TYPEV = self.primary.gettype()+'[]'

    def gettype(self):
        return self.TYPEV

    def constPropagationOpt(self):
        self.primary = self.primary.constPropagationOpt()
        self.exp = self.exp.constPropagationOpt()
        return self

class SEOPT:
    def __init__(self, se=''):
        self.se = se

    def genCode(self):
        if self.se:
            self.se.genCode()

    def constPropagationOpt(self):
        if self.se:
            self.se = self.se.constPropagationOpt()
        return self

class AEOPT:
    global intermediateCode
    def __init__(self, exp=''):
        self.exp = exp

    def genCode(self):
        if self.exp:
            self.exp.genCode()

    def constPropagationOpt(self):
        if self.exp:
            self.exp = self.exp.constPropagationOpt()
        return self

class SE:
    global intermediateCode
    def __init__(self, lhs, op='', exp=''):
        self.lhs = lhs
        self.exp = exp
        self.op = op
        self.type = 'se'
        self.TYPEV = ''

    def genCode(self):
        global currBlock, blockVar, mainFun, fun_param_dict, otherFun, fun_param_count
        if self.op:
            self.exp.genCode()
            ## Result of RHS will be in $t8 ##
            ## Perform the operations ##
            ## Handling '=' ##
            if self.op == '=':
                if self.lhs.type == 'variable':
                    if checkDeclaration(blockVar, currBlock, self.lhs.var) != 0:
                        if mainFun == 1:
                            intermediateCode.append('ori variable_%s, $t8, 0' %(self.lhs.var))
                        elif otherFun == 1:
                            if self.lhs.var in blockVar[0]:
                                intermediateCode.append('ori variable_%s, $t8, 0' %(self.lhs.var))
                            else:
                                if self.lhs.var in fun_param_dict:
                                    offset = fun_param_dict[self.lhs.var]
                                    intermediateCode.append('sw $t8, %s($s0)' %(offset))
                                else:
                                    [fun, offset] = fun_param_count.pop()
                                    fun_param_count.append([fun, offset+1])
                                    fun_param_dict[self.lhs.var] = (offset)*4
                                    intermediateCode.append('sw $t8, %s($s0)' %((offset)*4))
                    else:
                        ## This should not be the case for function calls ##
                        print "Error: Variable %s used but not declared.!" %(self.lhs.var)
                        sys.exit(-1)
                else:
                    ## Array ##
                    # if mainFun == 1:
                    ## I dont think this is necessary, if i handle in lhs, then it should be fine.. ##
                    intermediateCode.append('ori $a0, $t8, 0')
                    self.lhs.genCode()
                    ## Address to store the value will be in $t8 ##
                    intermediateCode.append('## Storing Register Values to Memory ##')
                    intermediateCode.append('sw $a0, 0($t8)')
                    # elif otherFun == 1:
                if (not self.exp.gettype() == 'input') and (self.lhs.gettype() != self.exp.gettype()) \
                        and (not (self.lhs.gettype() == 'int[][]' and self.exp.gettype() == 'int')):
                    print "Error: Type mismatch in the assignment.!"
                    sys.exit(-1)

            self.TYPEV = self.lhs.gettype()

        else:
            ## ++, -- will be handled here ##
            self.lhs.genCode()

    def gettype(self):
        if not self.TYPEV:
            self.TYPEV = self.lhs.gettype()
        return self.TYPEV

    ## Raj - Have to update ##
    def constPropagationOpt(self):
        global constantPropagation, optBlock, optBlockVar, constPropStack
        if self.op:
            self.exp = self.exp.constPropagationOpt()
            if self.lhs.type == 'variable' and (self.exp.type == 'num' or self.exp.gettype() == 'bool'):
                if optBlock in optBlockVar.keys():
                    optBlockVar[optBlock].append(self.lhs.var)
                else:
                    optBlockVar[optBlock] = [self.lhs.var]
                propDict = {}
                if optBlock in constPropStack.keys():
                    propDict = constPropStack.pop(optBlock)

                propDict[self.lhs.var] = self.exp.getValue()
                constPropStack[optBlock] = propDict
            else:
                print "[SE] LHS is an array.!"
        else:
            print "[SE] - Unary Operation -, !, ++, --"
            global loopblock
            self.lhs = self.lhs.constPropagationOpt()
            if loopblock == 0:
                return self.lhs

        return self

class Expression:
    global intermediateCode
    def __init__(self, exp):
        self.exp = exp
        self.type = 'ae'
        self.TYPEV = ''

    def genCode(self):
        # intermediateCode.append('EXPRESSION_START')
        ret = self.exp.genCode()
        self.TYPEV = self.exp.gettype()
        # intermediateCode.append('EXPRESSION_END')
        return ret

    def gettype(self):
        if not self.TYPEV:
            self.TYPEV = self.exp.gettype()
        return self.TYPEV

    def getValue(self):
        return self.exp.getValue()

    ## Raj - Have to update ##
    def constPropagationOpt(self):
        self.exp = self.exp.constPropagationOpt()
        if self.exp.type == 'num':
            return self.exp
        return self

class Primary:
    global intermediateCode
    def __init__(self, exp, lparen='', rparen=''):
        self.exp = exp
        self.lparen = lparen
        self.rparen = rparen
        self.type = 'primary'
        self.TYPEV = ''

    def genCode(self):
        if self.exp == 'true':
            intermediateCode.append('li $t8, 1')
            self.TYPEV = 'bool'
            return '1'
        elif self.exp == 'false':
            intermediateCode.append('li $t8, 1')
            self.TYPEV = 'bool'
            return '0'

        ret = self.exp.genCode()
        self.TYPEV = self.exp.gettype()
        return ret

    def gettype(self):
        if not self.TYPEV:
            if self.exp in ['true', 'false']:
                self.TYPEV = 'bool'
            else:
                self.TYPEV = self.exp.gettype()
        return self.TYPEV

    def getValue(self):
        if self.exp in ['true', 'false']:
            return self.exp
        elif self.exp.type == 'num':
            return self.exp

    ## Raj - Have to update ##
    def constPropagationOpt(self):
        if self.exp in ['true', 'false']:
            return self
        # elif self.exp == 'false':
        #     return Number(0)
        self.exp = self.exp.constPropagationOpt()
        if self.exp.type == 'num':
            return self.exp
        return self

class FUNCALL:
    global intermediateCode
    def __init__(self, id, arglist):
        self.arglist = arglist
        self.id = id
        self.type = 'funcall'

    def genCode(self):
        intermediateCode.append('## Function Call ##')
        # These calls are always non-main calls ##
        intermediateCode.append('la $s0, stack')
        self.arglist.genCode()
        intermediateCode.append('jal %s' %(self.id.var))

    def constPropagationOpt(self):
        return self

class ARGLIST:
    global intermediateCode, sta_arg
    def __init__(self, args=''):
        self.args = args
        self.type = 'arglist'

    def genCode(self):
        if self.args:
            self.args.genCode()

    ## Raj - Have to update ##
    def constPropagationOpt(self):
        return self

class ARGS:
    global intermediateCode
    def __init__(self, exp, args=''):
        self.args = args
        self.exp = exp
        self.type = 'args'

    def genCode(self):
        global sta_arg
        if sta_arg >= 8:
            print "Too many parameters for the function %s" %(self.exp.var)
            print "Max num of parameters supported : 8\nExitting.!"
            sys.exit(-1)
        self.exp.genCode()
        # intermediateCode.append('ori $s%s, $t8, 0' %(sta_arg))
        intermediateCode.append('sw $t8, %s($s0)' %(sta_arg*4))
        sta_arg += 1
        if self.args:
            self.args.genCode()
        sta_arg -= 1

    def constPropagationOpt(self):
        self.exp = self.exp.constPropagationOpt()
        if self.args:
            self.args = self.args.constPropagationOpt()
        return self

class ARRAY:
    global intermediateCode
    def __init__(self, new, type, dimexpr, dimstar):
        self.keyword = new
        self.TYPE = type
        self.dimexpr = dimexpr
        self.dimstar = dimstar
        self.type = 'array'
        self.TYPEV = ''

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
        self.TYPEV = self.TYPE.genCode()+self.dimexpr.gettype()
        if self.dimstar:
            self.TYPEV += self.dimstar.gettype()

    def gettype(self):
        return self.TYPEV

    ## Raj - Have to update ##
    def constPropagationOpt(self):
        return self

## Return Values ##
class Number:
    global intermediateCode
    def __init__(self, val):
        self.value = val
        self.type = 'num'
        self.TYPEV = 'int'

    def genCode(self):
        if int(self.value) >= 0:
            code = 'li $t8, %s' %(self.value)
            intermediateCode.append(code)
        else:
            intermediateCode.append('li $t8, %s' %str(0 - int(self.value)))
            intermediateCode.append('sub $t8, $zero, $t8')
        return str(self.value)

    def getValue(self):
        return str(self.value)

    def gettype(self):
        return self.TYPEV

    def constPropagationOpt(self):
        return self

## No Return values ##
class Unary_Ops:
    global intermediateCode
    def __init__(self, operator, operand, post=0):
        self.op = operator
        self.operand = operand
        self.type = 'uops'
        self.post= post
        self.TYPEV = ''

    def genCode(self):
        global intermediateCode, fun_param_count, fun_param_dict, currBlock
        intermediateCode.append('UNARY START')
        ## Either LHS or Array ##
        ret = self.operand.genCode()
        # print 'Return type of ret %s in unary ops: %s' %(ret, self.operand.gettype())
        if self.post == 0:
            ## Pre Operation ++i ##
            if self.op == '++':
                intermediateCode.append('addi $t9, $t8, 1')
                intermediateCode.append('ori $t8, $t9, 0')
                if self.operand.type == 'variable' or self.operand.type == 'lhs':
                    if typeChecking(ret, 'int', currBlock) == False:
                        print "Error: Unary operation ++ cannot be performed on %s.\nType Error." %(ret)
                        sys.exit(-1)

                    if mainFun == 1:
                        intermediateCode.append('ori variable_%s, $t9, 0' %(ret))
                    elif otherFun == 1:
                        if ret in blockVar[0]:
                            intermediateCode.append('ori variable_%s, $t9, 0' %(ret))
                        else:
                            if ret in fun_param_dict:
                                offset = fun_param_dict[ret]
                                intermediateCode.append('sw $t9, %s($s0)' %(offset))
                            else:
                                [fun, offset] = fun_param_count.pop()
                                fun_param_count.append([fun, offset+1])
                                fun_param_dict[ret] = (offset)*4
                                intermediateCode.append('sw $t9, %s($s0)' %((offset)*4))
                self.TYPEV = 'int'
            elif self.op == '--':
                intermediateCode.append('li $t9, 1')
                intermediateCode.append('sub $t9, $t8, $t9')
                intermediateCode.append('ori $t8, $t9, 0')
                if self.operand.type == 'variable' or self.operand.type == 'lhs':
                    if typeChecking(ret, 'int', currBlock) == False:
                        print "Error: Unary operation -- cannot be performed on %s.\nType Error." %(ret)
                        sys.exit(-1)
                    if mainFun == 1:
                        intermediateCode.append('ori variable_%s, $t9, 0' %(ret))
                    elif otherFun == 1:
                        if ret in blockVar[0]:
                            intermediateCode.append('ori variable_%s, $t9, 0' %(ret))
                        else:
                            if ret in fun_param_dict:
                                offset = fun_param_dict[ret]
                                intermediateCode.append('sw $t9, %s($s0)' %(offset))
                            else:
                                [fun, offset] = fun_param_count.pop()
                                fun_param_count.append([fun, offset+1])
                                fun_param_dict[ret] = (offset)*4
                                intermediateCode.append('sw $t9, %s($s0)' %((offset)*4))
                self.TYPEV = 'int'
            elif self.op == '-':
                if typeChecking(ret, 'int', currBlock) == False and self.operand.gettype() != 'int':
                    print "Error: Unary operation - cannot be performed on %s.\nType Error." %(ret)
                    sys.exit(-1)
                intermediateCode.append('sub $t9, $zero, $t8')
                intermediateCode.append('ori $t8, $t9, 0')
                self.TYPEV = 'int'
            elif self.op == '!':
                # print "Return Value : ", ret
                intermediateCode.append('seq $t9, $t8, $zero')
                intermediateCode.append('ori $t8, $t9, 0')
                self.TYPEV = 'bool'
        else:
            ## Post Operation i++ ##
            if self.op == '++':
                intermediateCode.append('addi $t9, $t8, 1')
                if self.operand.type == 'variable' or self.operand.type == 'lhs':
                    if typeChecking(ret, 'int', currBlock) == False:
                        print "Error: Unary operation ++ cannot be performed on %s.\nType Error." %(ret)
                        sys.exit(-1)
                    if mainFun == 1:
                        intermediateCode.append('ori variable_%s, $t9, 0' %(ret))
                    elif otherFun == 1:
                        if ret in blockVar[0]:
                            intermediateCode.append('ori variable_%s, $t9, 0' %(ret))
                        else:
                            if ret in fun_param_dict:
                                offset = fun_param_dict[ret]
                                intermediateCode.append('sw $t9, %s($s0)' %(offset))
                            else:
                                [fun, offset] = fun_param_count.pop()
                                fun_param_count.append([fun, offset+1])
                                fun_param_dict[ret] = (offset)*4
                                intermediateCode.append('sw $t9, %s($s0)' %((offset)*4))
                self.TYPEV = 'int'
            elif self.op == '--':
                intermediateCode.append('li $t9, 1')
                intermediateCode.append('sub $t9, $t8, $t9')
                if self.operand.type == 'variable' or self.operand.type == 'lhs':
                    if typeChecking(ret, 'int', currBlock) == False:
                        print "Error: Unary operation -- cannot be performed on %s.\nType Error." %(ret)
                        sys.exit(-1)
                    if mainFun == 1:
                        intermediateCode.append('ori variable_%s, $t9, 0' %(ret))
                    elif otherFun == 1:
                        if ret in blockVar[0]:
                            intermediateCode.append('ori variable_%s, $t9, 0' %(ret))
                        else:
                            if ret in fun_param_dict:
                                offset = fun_param_dict[ret]
                                intermediateCode.append('sw $t9, %s($s0)' %(offset))
                            else:
                                [fun, offset] = fun_param_count.pop()
                                fun_param_count.append([fun, offset+1])
                                fun_param_dict[ret] = (offset)*4
                                intermediateCode.append('sw $t9, %s($s0)' %((offset)*4))
                self.TYPEV = 'int'
            elif self.op == '-':
                if typeChecking(ret, 'int', currBlock) == False and self.operand.gettype() != 'int':
                    print "Error: Unary operation - cannot be performed on %s.\nType Error." %(ret)
                    sys.exit(-1)
                intermediateCode.append('sub $t9, $zero, $t8')
                intermediateCode.append('ori $t8, $t9, 0')
                self.TYPEV = 'int'
            elif self.op == '!':
                # print "Return Value : ", ret
                intermediateCode.append('seq $t9, $t8, $zero')
                intermediateCode.append('ori $t8, $t9, 0')
                self.TYPEV = 'bool'
        intermediateCode.append('UNARY END')

    def gettype(self):
        if not self.TYPEV:
            self.TYPEV = self.operand.gettype()
        return self.TYPEV

    ## Raj - Have to update ##
    def constPropagationOpt(self):
        global constPropStack, optBlock, optBlockVar
        constantPropagation = {}
        if optBlock in constPropStack.keys():
            constantPropagation = constPropStack[optBlock]

        # Operators: ++, --, -, !
        temp = copy.deepcopy(self.operand)
        self.operand = self.operand.constPropagationOpt()
        if self.operand.type == 'variable' and \
            checkIfVarInStackDict(self.operand, constPropStack, optBlock):
            if self.op in  ['++', '--']:
                print "Variable is no longer a constant.!"
            else:
                # val = constantPropagation[self.operand]
                val = getLatestValFromStackDict(self.operand, constPropStack, optBlock)
                if self.op == '!':
                    if val == 0:
                        return Primary('true')
                    else:
                        return Primary('false')
                elif self.op == '-':
                    ## z = -2 - should be a const ##
                    # return Unary_Ops('-',Number(val))
                    return Number(0 - int(val))
        elif self.operand.type == 'lhs':
            # The below is good, but the actual value should be updated ##
            # x = z++; -> z should be updated to z+1 value #

            res = 0
            if self.operand.id_or_array.type == 'num':
                if self.post == 1:
                    if self.op == '++':
                        res = int(self.operand.id_or_array.getValue()) + 1
                        if optBlock in optBlockVar.keys():
                            optBlockVar[optBlock].append(temp.id_or_array.var)
                        else:
                            optBlockVar[optBlock] = [temp.id_or_array.var]
                        propDict = {}
                        if optBlock in constPropStack.keys():
                            propDict = constPropStack.pop(optBlock)

                        propDict[temp.id_or_array.var] = res
                        constPropStack[optBlock] = propDict
                        if loopblock == 0:
                            return Number(int(self.operand.id_or_array.getValue()))
                    elif self.op == '--':
                        res = int(self.operand.id_or_array.getValue()) - 1
                        if optBlock in optBlockVar.keys():
                            optBlockVar[optBlock].append(temp.id_or_array.var)
                        else:
                            optBlockVar[optBlock] = [temp.id_or_array.var]
                        propDict = {}
                        if optBlock in constPropStack.keys():
                            propDict = constPropStack.pop(optBlock)

                        propDict[temp.id_or_array.var] = res
                        constPropStack[optBlock] = propDict
                        if loopblock == 0:
                            return Number(int(self.operand.id_or_array.getValue()))
                else:
                    if self.op == '++':
                        res = int(self.operand.id_or_array.getValue()) + 1
                        if optBlock in optBlockVar.keys():
                            optBlockVar[optBlock].append(temp.id_or_array.var)
                        else:
                            optBlockVar[optBlock] = [temp.id_or_array.var]
                        propDict = {}
                        if optBlock in constPropStack.keys():
                            propDict = constPropStack.pop(optBlock)

                        propDict[temp.id_or_array.var] = res
                        constPropStack[optBlock] = propDict
                        if loopblock == 0:
                            return Number(res)
                    elif self.op == '--':
                        res = int(self.operand.id_or_array.getValue())-1
                        if optBlock in optBlockVar.keys():
                            optBlockVar[optBlock].append(temp.id_or_array.var)
                        else:
                            optBlockVar[optBlock] = [temp.id_or_array.var]
                        propDict = {}
                        if optBlock in constPropStack.keys():
                            propDict = constPropStack.pop(optBlock)

                        propDict[temp.id_or_array.var] = res
                        constPropStack[optBlock] = propDict
                        if loopblock == 0:
                            if res >= 0:
                                return Number(int(self.operand.id_or_array.getValue())-1)
                            else:
                                # return Unary_Ops('-', Number(0-res), self.post)
                                return Number(res)
        if loopblock != 0:
            self.operand = temp
        return self

## No Return values ##
class Bin_Ops:
    global intermediateCode
    def __init__(self, left, operator, right):
        self.type = 'binop'
        self.left = left
        self.right = right
        self.op = operator
        self.TYPEV = ''

    def genCode(self):
        self.left.genCode()
        if self.op == '+':
            intermediateCode.append('ori $t9, $t8, 0')
            self.right.genCode()
            intermediateCode.append('add $v0, $t9, $t8')
            intermediateCode.append('ori $t8, $v0, 0')
            self.TYPEV = 'int'
        elif self.op == '-':
            intermediateCode.append('ori $t9, $t8, 0')
            self.right.genCode()
            intermediateCode.append('sub $v0, $t9, $t8')
            intermediateCode.append('ori $t8, $v0, 0')
            self.TYPEV = 'int'
        elif self.op == '*':
            intermediateCode.append('ori $v0, $t8, 0')
            self.right.genCode()
            intermediateCode.append('mult $t8, $v0')
            intermediateCode.append('mflo $t8')
            self.TYPEV = 'int'
        elif self.op == '/':
            intermediateCode.append('ori $v0, $t8, 0')
            self.right.genCode()
            intermediateCode.append('div $t8, $v0')
            intermediateCode.append('mflo $t8')
            self.TYPEV = 'int'
        elif self.op == '%':
            intermediateCode.append('ori $v0, $t8, 0')
            self.right.genCode()
            intermediateCode.append('div $t8, $v0')
            intermediateCode.append('mfhi $t8')
            self.TYPEV = 'int'
        elif self.op == '||':
            intermediateCode.append('sne $t9, $t8, $zero')
            intermediateCode.append('bgez $t9, __LABEL__')
            ## Should Peek ##
            self.right.genCode()
            intermediateCode.append('sne $t9, $t8, $zero')
            intermediateCode.append('__POP__LABEL__')
            intermediateCode.append('ori $t8, $t9, 0')
            self.TYPEV = 'bool'
        elif self.op == '&&':
            intermediateCode.append('sne $t9, $t8, $zero')
            intermediateCode.append('beq $t9, $zero, __LABEL__')
            ## Should Peek ##
            self.right.genCode()
            intermediateCode.append('sne $t9, $t8, $zero')
            intermediateCode.append('__POP__LABEL__')
            intermediateCode.append('ori $t8, $t9, 0')
            self.TYPEV = 'bool'
        elif self.op == '==':
            intermediateCode.append('ori $t9, $t8, 0')
            self.right.genCode()
            intermediateCode.append('seq $v0, $t9, $t8')
            intermediateCode.append('ori $t8, $v0, 0')
            self.TYPEV = 'bool'
        elif self.op == '!=':
            intermediateCode.append('ori $t9, $t8, 0')
            self.right.genCode()
            intermediateCode.append('sne $v0, $t9, $t8')
            intermediateCode.append('ori $t8, $v0, 0')
            self.TYPEV = 'bool'
        elif self.op == '<':
            intermediateCode.append('ori $t9, $t8, 0')
            self.right.genCode()
            intermediateCode.append('slt $v0, $t9, $t8')
            intermediateCode.append('ori $t8, $v0, 0')
            self.TYPEV = 'bool'
        elif self.op == '<=':
            intermediateCode.append('ori $t9, $t8, 0')
            self.right.genCode()
            intermediateCode.append('sle $v0, $t9, $t8')
            intermediateCode.append('ori $t8, $v0, 0')
            self.TYPEV = 'bool'
        elif self.op == '>':
            intermediateCode.append('ori $t9, $t8, 0')
            self.right.genCode()
            intermediateCode.append('sgt $v0, $t9, $t8')
            intermediateCode.append('ori $t8, $v0, 0')
            self.TYPEV = 'bool'
        elif self.op == '>=':
            intermediateCode.append('ori $t9, $t8, 0')
            self.right.genCode()
            intermediateCode.append('sge $v0, $t9, $t8')
            intermediateCode.append('ori $t8, $v0, 0')
            self.TYPEV = 'bool'
        if self.left.gettype() != self.right.gettype():
            print "Error: Binary operation of non-matched type variables.!"
            sys.exit(-1)

    def gettype(self):
        return self.TYPEV

    ## Raj - Have to update ##
    def constPropagationOpt(self):
        # if self.left.exp.type == 'variable':
        self.left = self.left.constPropagationOpt()
        self.right = self.right.constPropagationOpt()
        if self.left.type == 'num' and self.right.type == 'num':
            if self.op == '+':
                res = int(self.left.value) + int(self.right.value)
                return Number(res)
            elif self.op == '-':
                res = int(self.left.value) - int(self.right.value)
                if res >= 0:
                    return Number(res)
                else:
                    return Unary_Ops('-',Number(0 - res))
            elif self.op == '*':
                res = int(self.left.value) * int(self.right.value)
                return Number(res)
            elif self.op == '/':
                res = int(self.left.value) / int(self.right.value)
                return Number(res)
            elif self.op == '%':
                res = int(self.left.value) % int(self.right.value)
                return Number(res)
            elif self.op == '||':
                if int(self.left.value) != 0 or int(self.right.value) != 0:
                    return Number(1)
                else:
                    return Number(0)
            elif self.op == '&&':
                if int(self.left.value) != 0 and int(self.right.value) != 0:
                    return Number(1)
                else:
                    return Number(0)
            elif self.op == '==':
                if int(self.left.value) == int(self.right.value):
                    return Number(1)
                else:
                    return Number(0)
            elif self.op == '!=':
                if int(self.left.value) != int(self.right.value):
                    return Number(1)
                else:
                    return Number(0)
            elif self.op == '<':
                if int(self.left.value) < int(self.right.value):
                    return Number(1)
                else:
                    return Number(0)
            elif self.op == '<=':
                if int(self.left.value) <= int(self.right.value):
                    return Number(1)
                else:
                    return Number(0)
            elif self.op == '>':
                if int(self.left.value) > int(self.right.value):
                    return Number(1)
                else:
                    return Number(0)
            elif self.op == '>=':
                if int(self.left.value) >= int(self.right.value):
                    return Number(1)
                else:
                    return Number(0)
        return self

## Return Values ##
class Names:
    global intermediateCode
    def __init__(self, var):
        self.var = var
        self.type = 'variable'
        self.TYPEV = ''

    def genCode(self):
        global currBlock, blockVar, declared, fun_param_count, fun_param_dict
        self.TYPEV = getTypes(self.var, currBlock)
        if declared == 1 or checkDeclaration(blockVar, currBlock, self.var):
            if mainFun == 1:
                intermediateCode.append('ori $t8, variable_%s, 0' %(self.var))
            elif otherFun == 1:
                if self.var in blockVar[0]:
                    intermediateCode.append('ori $t8, variable_%s, 0' %(self.var))
                else:
                    if self.var in fun_param_dict:
                        offset = fun_param_dict[self.var]
                        intermediateCode.append('lw $t8, %s($s0)' %(offset))
                    else:
                        [fun, offset] = fun_param_count.pop()
                        fun_param_count.append([fun, offset+1])
                        fun_param_dict[self.var] = (offset)*4
                        intermediateCode.append('lw $t8, %s($s0)' %((offset)*4))
            return self.var
        else:
            print "Error: Variable %s used but not declared.!" %(self.var)
            sys.exit(-1)

    def gettype(self):
        if not self.TYPEV:
            self.TYPEV = getTypes(self.var, currBlock)
        return self.TYPEV

    ## Raj - Have to update ##
    def constPropagationOpt(self):
        global constPropStack, optBlock
        # constantPropagation = {}
        # if optBlock in constPropStack.keys():
        #     constantPropagation = constPropStack[optBlock]

        if checkIfVarInStackDict(self.var, constPropStack, optBlock):
            val = getLatestValFromStackDict(self.var, constPropStack, optBlock)
            if val:
                # if loopblock == 0:
                return Number(val)

        return self

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

    ## Raj - Have to update ##
    def constPropagationOpt(self):
        global  optBlock, constPropStack, optBlockVar
        self.exp = self.exp.constPropagationOpt()
        optBlock += 1
        ## Actual Updates here ##
        self.stmt = self.stmt.constPropagationOpt()
        try:
            constPropStack.pop(optBlock)
        except KeyError:
            pass
        ## Handle Variables Here ##
        # print "Variables Raj: ", constPropStack
        # print "Variables Raj: ", optBlockVar[optBlock]
        if optBlock in optBlockVar.keys():
            for var in optBlockVar[optBlock]:
                for i in range(optBlock+1):
                    try:
                        removeEntryFromDict(var, constPropStack[i])
                    except KeyError:
                        pass
        # print "Variables Raj: ", constPropStack
        # print "Variables Raj: ", optBlockVar[optBlock]
        if optBlock in optBlockVar.keys():
            optBlockVar.pop(optBlock)

        optBlock -= 1

        return self

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

    ## Have to update - Done ##
    def constPropagationOpt(self):
        global  optBlock, constPropStack, optBlockVar
        ifDict = {}
        elseDict = {}
        self.exp = self.exp.constPropagationOpt()
        optBlock += 1
        ## Actual Updates here ##
        self.stmt1 = self.stmt1.constPropagationOpt()
        try:
            ifDict = constPropStack.pop(optBlock)
        except KeyError:
            pass
        ## Handle Variables Here ##
        # print "IF - Variables Raj: ", constPropStack
        # print "IF - Variables Raj: ", optBlockVar[optBlock]
        try:
            optBlockVar.pop(optBlock)
        except KeyError:
            pass
        ## Actual Updates here ##
        self.stmt2 = self.stmt2.constPropagationOpt()
        try:
            elseDict = constPropStack.pop(optBlock)
        except KeyError:
            pass
        ## Handle Variables Here ##
        # print "ELSE - Variables Raj: ", constPropStack
        # print "ELSE - Variables Raj: ", optBlockVar[optBlock]

        ifset = set(ifDict.keys())
        elseset = set(elseDict.keys())
        inter = ifset.intersection(elseset)
        # ifset = ifset.difference(inter)
        # elseset = elseset.difference(inter)
        tempset = ifset.union(elseset)
        uset = tempset.difference(inter)
        for var in uset:
            for i in range(optBlock+1):
                try:
                    removeEntryFromDict(var, constPropStack[i])
                except KeyError:
                    pass
        # Update the dictionary with the intersection values #
        for var in inter:
            if ifDict[var] == elseDict[var]:
                # Update the dict with the new value
                for i in range(optBlock):
                    constPropStack[i][var] = ifDict[var]
                    # print "Common val: ", var, ifDict[var], elseDict[var], constPropStack
            else:
                # Remove the entry from dict #
                for i in range(optBlock):
                    try:
                        removeEntryFromDict(var, constPropStack[i])
                    except KeyError:
                        pass
                # print "To be removed common val: ", var, ifDict[var], elseDict[var], constPropStack
        if optBlock in optBlockVar.keys():
            optBlockVar.pop(optBlock)
        optBlock -= 1
        return self

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

    def constPropagationOpt(self):
        global optBlock, constPropStack, loopblock
        self.exp = self.exp.constPropagationOpt()

        optBlock += 1
        loopblock += 1
        ## Actual Updates here ##
        # oldStmt = copy.deepcopy(self.stmt)
        self.stmt = self.stmt.constPropagationOpt()
        # self.stmt = oldStmt
        try:
            constPropStack.pop(optBlock)
        except KeyError:
            pass
        ## Handle Variables Here ##
        if optBlock in optBlockVar.keys():
            for var in optBlockVar[optBlock]:
                for i in range(optBlock+1):
                    try:
                        removeEntryFromDict(var, constPropStack[i])
                    except KeyError:
                        pass
        if optBlock in optBlockVar.keys():
            optBlockVar.pop(optBlock)

        loopblock -= 1
        optBlock -= 1


        return self

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

    ## Raj - Have to update ##
    def constPropagationOpt(self):
        if self.seopt1:
            self.seopt1 = self.seopt1.constPropagationOpt()
        if self.aeopt:
            self.aeopt = self.aeopt.constPropagationOpt()

        global optBlock, constPropStack, loopblock
        optBlock += 1
        loopblock += 1

        ## Actual Updates here ##
        self.stmt = self.stmt.constPropagationOpt()
        try:
            constPropStack.pop(optBlock)
        except KeyError:
            pass
        ## Handle Variables Here ##
        if optBlock in optBlockVar.keys():
            for var in optBlockVar[optBlock]:
                for i in range(optBlock+1):
                    try:
                        removeEntryFromDict(var, constPropStack[i])
                    except KeyError:
                        pass
        if optBlock in optBlockVar.keys():
            optBlockVar.pop(optBlock)

        loopblock -= 1
        optBlock -= 1

        if self.seopt2:
            self.seopt2 = self.seopt2.constPropagationOpt()
        return self

class DO_WHILE:
    global intermediateCode
    def __init__(self, stmt, exp):
        self.exp = exp
        self.stmt = stmt
        self.type = 'do_while'

    def genCode(self):
        intermediateCode.append('BRANCH LABEL_DO_WHILE')
        intermediateCode.append('__DO_WHILE_LABEL_START__')
        self.stmt.genCode()
        self.exp.genCode()
        intermediateCode.append('bne $t8, $zero, __DO_WHILE_LABEL__')
        intermediateCode.append('b __DO_WHILE_LABEL_START__')
        ## POP-1 While Label ##
        intermediateCode.append('BRANCH LABEL_DO_WHILE_END')
        ## POP-2 While Label ##
        intermediateCode.append(';')

    ## Raj - Have to update ##
    def constPropagationOpt(self):
        global optBlock, constPropStack, loopblock
        optBlock += 1
        loopblock += 1
        ## Actual Updates here ##
        self.stmt = self.stmt.constPropagationOpt()
        try:
            constPropStack.pop(optBlock)
        except KeyError:
            pass
        ## Handle Variables Here ##
        if optBlock in optBlockVar.keys():
            for var in optBlockVar[optBlock]:
                for i in range(optBlock+1):
                    try:
                        removeEntryFromDict(var, constPropStack[i])
                    except KeyError:
                        pass
        if optBlock in optBlockVar.keys():
            optBlockVar.pop(optBlock)
        loopblock += 1
        optBlock -= 1

        self.exp = self.exp.constPropagationOpt()

        return self

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
    'pgm : declseq'
    p[0] = Program(p[1])

def p_declseq(p):
    '''declseq : declare declseq
               | '''
    if len(p) == 3:
        p[0] = DECLSEQ(p[1], p[2])

## Decl ##
def p_declare(p):
    '''declare : decl
               | funDecl'''
    p[0] = DECLARE(p[1])

## VarDecl ##
def p_decl(p):
    'decl : type varlist SEMICOLON'
    if len(p) == 4:
        p[0] = DECL(p[1], p[2])

def p_type(p):
    '''type : INT
           | BOOL
           | VOID
           | type LSQUAREBRACE RSQUAREBRACE'''
    p[0] = TYPE(p[1])

def p_varlist(p):
    '''varlist : var COMMA varlist
              | var'''
    if len(p) == 4:
        p[0] = VARLIST(p[1], p[2], p[3])
    elif len(p) == 2:
        p[0] = VARLIST(p[1])

def p_fundecl(p):
    'funDecl : type ID LPAREN FORMALS RPAREN stmt'
    p[0] = FUNDECL(p[1], Names(p[2]), p[6], p[4])

## Raj ##
def p_formals(p):
    '''FORMALS : FORMAL
               | '''
    if len(p) > 1:
        p[0] = FORMALS(p[1])

## Raj ##
def p_formal(p):
    '''FORMAL : type ID COMMA FORMAL
            | type ID'''
    if len(p) == 5:
        p[0] = Formal(p[1], Names(p[2]), p[4])
    else:
        p[0] = Formal(p[1], Names(p[2]))

def p_stmt(p):
    '''stmt : SE SEMICOLON
            | print
            | block
            | if
            | while
            | for
            | do_while
            | return_stmt'''
    p[0] = Statement(p[1])

def p_ret_stmt(p):
    '''return_stmt : RETURN SEMICOLON
                   | RETURN expression SEMICOLON'''
    if len(p) == 4:
        p[0] = RETURN(p[2])
    else:
        p[0] = RETURN()

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

def p_aeopt(p):
    '''AEOpt : expression
            | '''
    if len(p) == 2:
        p[0] = AEOPT(p[1])

def p_var(p):
    'var : ID'
    p[0] = VAR(p[1])

def p_se(p):
    '''SE : lhs EQL expression
          | prepost
          | FunctionCall'''
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
    '''lhs : arrayAccess'''
    # names[p[1]] = p[3]
    p[0] = LHS(p[1])

def p_arrayAccess(p):
    'arrayAccess : Primary LSQUAREBRACE expression RSQUAREBRACE'
    p[0] = ArrayAccess(p[1], p[3])

def p_expression(p):
    '''expression : SE
                  | Primary
                  | array'''
    p[0] = Expression(p[1])

def p_primary(p):
    '''Primary : TRUE
               | FALSE
               | input
               | LPAREN expression RPAREN
               | arrayAccess'''
    if len(p) == 2:
        p[0] = Primary(p[1])
    else:
        p[0] = Primary(p[2], p[1], p[3])

def p_primary_id(p):
    'Primary : ID'
    p[0] = Primary(Names(p[1]))

def p_functionCall(p):
    '''FunctionCall : ID LPAREN ARGLIST RPAREN'''
    p[0] = FUNCALL(Names(p[1]), p[3])

def p_arglist(p):
    '''ARGLIST : ARGS
               | '''
    if len(p) == 2:
        p[0] = ARGLIST(p[1])
    else:
        p[0] = ARGLIST()

## Change Raj ##
def p_args(p):
    '''ARGS : expression COMMA ARGS
            | expression'''
    if len(p) == 4:
        p[0] = ARGS(p[1], p[3])
    else:
        p[0] = ARGS(p[1])

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
    'block : LBRACE vardeclseq stmtseq RBRACE'
    p[0] = Block(p[2], p[3])

## Raj ##
def p_vardeclseq(p):
    '''vardeclseq : decl vardeclseq
                  | '''
    if len(p) == 3:
        p[0] = VARDECLSEQ(p[1], p[2])

## Raj ##
def p_stmtseq(p):
    '''stmtseq : stmt stmtseq
               | '''
    if len(p) == 3:
        p[0] = Statements(p[1], p[2])

## Expressions Parsing ##
## This is the only way to define UMINUS ##
def p_expression_uminus(p):
    'expression  : MINUS expression %prec UMINUS'
    p[0] = Unary_Ops(p[1], Expression(p[2]))

def p_expression_unary(p):
    'expression : NOT expression'
    p[0] = Unary_Ops(p[1], Expression(p[2]))

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

def run(data, copypropogation, constpropagation, loopinvariant, commonsubexpelim):
    global intermediateCode, constantPropagation
    parser = yacc.yacc()
    result = parser.parse(data)

    if copypropogation == 1:
        ## Perform Copy Propagation
        print "[copypropogation] Not Implemented yet.!"

    if constpropagation == 1:
        ## Perform Constant Propagation
        # print "[constpropagation] Not Implemented yet.!"
        result = result.constPropagationOpt()

    if loopinvariant == 1:
        ## Perform Loop Invariant optimization
        print "[loopinvariant] Not Implemented yet.!"

    if commonsubexpelim == 1:
        ## Perform Common Sub-exp Elimination
        print "[commonsubexpelim] Not Implemented yet.!"

    # print constantPropagation

    if result:
        print "Parsing Completed.!"
    else:
        print "Syntax Check Failed.!\nExitting.!"
        sys.exit(-1)

    result.genCode()
    global blockVar, fun_param_count, fun_param_dict
    print "Block Var: ", blockVar
    print "Count Dict: ", fun_param_count
    print "Param Func: ", fun_param_dict
    print "Types Dict: ", types
    # sys.exit(-1)
