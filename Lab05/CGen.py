##########################################################################################################
## Class: CodeGen											                                            ##
## This class is responsible to generate the final code (XXX.asm) file 					                ##
## 													                                                    ##
##													                                                    ##
## Name: 	Rajendra Kumar Raghupatruni		    						                                ##
## SBU Net ID: 	rraghuaptrun				    						                                ##
## SBU ID: 	109785402				    						                                        ##
##########################################################################################################

import re, sys

class CodeGen:
    def __init__(self, asmfile, allocReg, stmt):
        self.get = 10
        self.asmfid = open(asmfile,'w')
        self.allocReg = allocReg
        self.Dict = {}
        self.stmt = stmt
        self.ic = []
        # self.unusedVar = remVar
        self.labelCount = 0
        self.labelStack = []
        self.ifLabelStack = []
        self.loopLabelStack = []
        self.loop2LabelStack = []
        self.codeStack = []

    def genLabel(self):
        ret = 'LABEL%s' %self.labelCount
        self.labelCount += 1
        return ret

    def peekLabel(self, type):
        if type == 'if':
            return self.ifLabelStack[-1]
        elif type == 'while':
            return self.loopLabelStack[-1]
        elif type == 'loop2':
            return self.loop2LabelStack[-1]

    ## Deprecated ##
    ## Sbrk system call - To Allocate memory ##
    def allocMem(self, bytes):
        return '; ## Allocating Memory ##; li $a0, %s; li $v0, 9; syscall;;' %(bytes)

    def generateHeaders(self):
        self.asmfid.write(".globl main\n")
        self.asmfid.write("\n.data\n   str4: .asciiz \"\\n\" \n   memory: .word 0 1 2 3 4\n   stack: .word 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15\n\n")
        self.asmfid.write("\n.text\n")
        # self.asmfid.write("main:\n")

    def getExit(self):
        return ';exit:; ## Exit ##; la $a0, str4; li $v0, 4; syscall;; li $v0, 10; syscall;;'

    ## Deprecated ##
    def inputInt(self):
        return '; ## Reading input from stdin ##;   li $v0, 5;   syscall; ## End of reading Input ##;'

    ## Deprecated ##
    def printInt(self):
        return '; ## Adding New Line ##; ori $t8, $a0, 0; la $a0, str4; li $v0, 4; syscall;; ## Printing Integer ##; ori $a0, $t8, 0; li $v0, 1; syscall; ## End of Print ##;'

    ## Deprecated ##
    def evalBinExp(self, var1, var2, op):
        ret = ''
        reg = ''
        if op == '+':
            if re.search('^[0-9]+$', var1):
                ret += "; li $t8, %s;" %(var1)
                if re.search('^[0-9]+$', var2):
                    ret += "; addi $v0, $t8, $%s;" %(var2)
                else:
                    if re.match('^\$', var2):
                        ret += "; add $v0, $t8, %s;" %(var2)
                    else:
                        ret += "; add $v0, $t8, $%s;" %(self.allocReg[var2])
            else:
                if re.match('^\$', var1):
                    ret += "; ori $t8, %s, 0;" %(var1)
                else:
                    ret += "; ori $t8, $%s, 0;" %(self.allocReg[var1])
                if re.search('^[0-9]+$', var2):
                    ret += "; addi $v0, $t8, %s;" %(var2)
                else:
                    if re.match('^\$', var2):
                        ret += "; add $v0, $t8, %s;" %var2
                    else:
                        ret += "; add $v0, $t8, $%s;" %(self.allocReg[var2])
            reg = '$v0'
        elif op == '-':
            if re.search('^[0-9]+$', var1):
                ret += "; li $t8, %s;" %(var1)
                if re.search('^[0-9]+$', var2):
                    ret += "; li $t9, %s; sub $v0, $t8, $t9;" %(var2)
                else:
                    if re.match('^\$', var2):
                        ret += "; sub $v0, $t8, %s;" %(var2)
                    else:
                        ret += "; sub $v0, $t8, $%s;" %(self.allocReg[var2])
            else:
                if re.match('^\$', var1):
                    ret += "; ori $t8, %s, 0;" %(var1)
                else:
                    ret += "; ori $t8, $%s, 0;" %(self.allocReg[var1])
                if re.search('^[0-9]+$', var2):
                    ret += "; li $t9, %s; sub $v0, $t8, $t9;" %(var2)
                else:
                    if re.match('^\$', var2):
                        ret += "; sub $v0, $t8, %s;" %(var2)
                    else:
                        ret += "; sub $v0, $t8, $%s;" %(self.allocReg[var2])
            reg = '$v0'
        elif op == '*':
            if re.search('^[0-9]+$', var1):
                ret += "; li $t8, %s;" %(var1)
                if re.search('^[0-9]+$', var2):
                    ret += "; li $t9, %s; mult $t8, $t9;" %(var2)
                else:
                    if re.match('^\$', var2):
                        ret += "; mult $t8, %s;" %(var2)
                    else:
                        ret += "; mult $t8, $%s;" %(self.allocReg[var2])
            else:
                if re.match('^\$', var1):
                    ret += "; ori $t8, %s, 0;" %(var1)
                else:
                    ret += "; ori $t8, $%s, 0;" %(self.allocReg[var1])
                if re.search('^[0-9]+$', var2):
                    ret += "; li $t9, %s; mult $t8, $t9;" %(var2)
                else:
                    if re.match('^\$', var2):
                        ret += "; mult $t8, %s;" %(var2)
                    else:
                        ret += "; mult $t8, $%s;" %(self.allocReg[var2])
            reg = '$LO'
        elif op == '/' or op == '%':
            if re.search('^[0-9]+$', var1):
                ret += "; li $t8, %s;" %(var1)
                if re.search('^[0-9]+$', var2):
                    ret += "; li $t9, %s; div $t8, $t9;" %(var2)
                else:
                    if re.match('^\$', var2):
                        ret += "; div $t8, %s;" %(var2)
                    else:
                        ret += "; div $t8, $%s;" %(self.allocReg[var2])
            else:
                if re.match('^\$', var1):
                    ret += "; ori $t8, %s, 0;" %(var1)
                else:
                    ret += "; ori $t8, $%s, 0;" %(self.allocReg[var1])
                if re.search('^[0-9]+$', var2):
                    ret += "; li $t9, %s; div $t8, $t9;" %(var2)
                else:
                    if re.match('^\$', var2):
                        ret += "; div $t8, %s;" %(var2)
                    else:
                        ret += "; div $t8, $%s;" %(self.allocReg[var2])
            if op == '/':
                reg = '$LO'
            else:
                reg = '$HI'
        elif op == '||':
            if re.search('^[0-9]+$', var1):
                ret += "; li $t8, %s;" %(var1)
                if re.search('^[0-9]+$', var2):
                    ret += "; li $v0, %s;" %(var2)
                else:
                    if re.match('^\$', var2):
                        ret += "; ori $v0, %s, $zero;;" %(var2)
                    else:
                        ret += "; ori $v0, $%s, $zero;;" %(self.allocReg[var2])
                ret += '; sne $t9, $t8, $zero; bgez $t9, LABEL%s;' %(self.labelCount)
                self.labelStack.append('LABEL%s:;' %self.labelCount)
                self.labelCount += 1
                ret += "; sne $t9, $v0, $zero;;"
                ret += self.labelStack.pop()
            else:
                if re.match('^\$', var1):
                    ret += "; ori $t8, %s, 0;" %(var1)
                else:
                    ret += "; ori $t8, $%s, 0;" %(self.allocReg[var1])

                if re.search('^[0-9]+$', var2):
                    ret += "; li $v0, %s;" %(var2)
                else:
                    if re.match('^\$', var2):
                        ret += "; ori $v0, %s, $zero;" %(var2)
                    else:
                        ret += "; ori $v0, $%s, $zero;" %(self.allocReg[var2])
                ret += '; sne $t9, $t8, $zero; bgez $t9, LABEL%s;' %(self.labelCount)
                self.labelStack.append('LABEL%s:;' %self.labelCount)
                self.labelCount += 1
                ret += "; sne $t9, $v0, $zero;"
                ret += self.labelStack.pop()
            reg = '$t9'

        elif op == '&&':
            if re.search('^[0-9]+$', var1):
                ret += "; li $t8, %s;" %(var1)
                if re.search('^[0-9]+$', var2):
                    ret += "; li $v0, %s;" %(var2)
                else:
                    if re.match('^\$', var2):
                        ret += "; ori $v0, %s, $zero;;" %(var2)
                    else:
                        ret += "; ori $v0, $%s, $zero;;" %(self.allocReg[var2])
                ret += '; sne $t9, $t8, $zero; beq $t9, $zero, LABEL%s;' %(self.labelCount)
                self.labelStack.append('LABEL%s:;' %self.labelCount)
                self.labelCount += 1
                ret += "; sne $t9, $v0, $zero;;"
                ret += self.labelStack.pop()
            else:
                if re.match('^\$', var1):
                    ret += "; ori $t8, %s, 0;" %(var1)
                else:
                    ret += "; ori $t8, $%s, 0;" %(self.allocReg[var1])

                if re.search('^[0-9]+$', var2):
                    ret += "; li $v0, %s;" %(var2)
                else:
                    if re.match('^\$', var2):
                        ret += "; ori $v0, %s, 0;" %(var2)
                    else:
                        ret += "; ori $v0, $%s, 0;" %(self.allocReg[var2])
                ret += '; sne $t9, $t8, $zero; beq $t9, $zero, LABEL%s;' %(self.labelCount)
                self.labelStack.append('LABEL%s:;' %self.labelCount)
                self.labelCount += 1
                ret += "; sne $t9, $v0, $zero;"
                ret += self.labelStack.pop()
            reg = '$t9'
        elif op == '==':
            if re.search('^[0-9]+$', var1):
                ret += "; li $t8, %s;" %(var1)

                if re.search('^[0-9]+$', var2):
                    ret += "; li $t9, %s; seq $v0, $t8, $t9;" %(var2)
                else:
                    if re.match('^\$', var2):
                        ret += "; seq $v0, $t8, %s;" %(var2)
                    else:
                        ret += "; seq $v0, $t8, $%s;" %(self.allocReg[var2])
            else:
                if re.match('^\$', var1):
                    ret += "; ori $t8, %s, 0;" %(var1)
                else:
                    ret += "; ori $t8, $%s 0;" %(self.allocReg[var1])

                if re.search('^[0-9]+$', var2):
                    ret += "; li $t9, %s; seq $v0, $t8, $t9;" %(var2)
                else:
                    if re.match('^\$', var2):
                        ret += "; seq $v0, $t8, %s;" %(var2)
                    else:
                        ret += "; seq $v0, $t8, $%s;" %(self.allocReg[var2])
            reg = '$v0'
        elif op == '!=':
            if re.search('^[0-9]+$', var1):
                ret += "; li $t8, %s;" %(var1)

                if re.search('^[0-9]+$', var2):
                    ret += "; li $t9, %s; sne $v0, $t8, $t9;" %(var2)
                else:
                    if re.match('^\$', var2):
                        ret += "; sne $v0, $t8, %s;" %(var2)
                    else:
                        ret += "; sne $v0, $t8, $%s;" %(self.allocReg[var2])
            else:
                if re.match('^\$', var1):
                    ret += "; ori $t8, %s, 0;" %(var1)
                else:
                    ret += "; ori $t8, $%s 0;" %(self.allocReg[var1])

                if re.search('^[0-9]+$', var2):
                    ret += "; li $t9, %s; sne $v0, $t8, $t9;" %(var2)
                else:
                    if re.match('^\$', var2):
                        ret += "; sne $v0, $t8, %s;" %(var2)
                    else:
                        ret += "; sne $v0, $t8, $%s;" %(self.allocReg[var2])
            reg = '$v0'
        elif op == '<':
            if re.search('^[0-9]+$', var1):
                ret += "; li $t8, %s;" %(var1)

                if re.search('^[0-9]+$', var2):
                    ret += "; li $t9, %s; slt $v0, $t8, $t9;" %(var2)
                else:
                    if re.match('^\$', var2):
                        ret += "; slt $v0, $t8, %s;" %(var2)
                    else:
                        ret += "; slt $v0, $t8, $%s;" %(self.allocReg[var2])
            else:
                if re.match('^\$', var1):
                    ret += "; ori $t8, %s, 0;" %(var1)
                else:
                    ret += "; ori $t8, $%s 0;" %(self.allocReg[var1])

                if re.search('^[0-9]+$', var2):
                    ret += "; li $t9, %s; slt $v0, $t8, $t9;" %(var2)
                else:
                    if re.match('^\$', var2):
                        ret += "; slt $v0, $t8, %s;" %(var2)
                    else:
                        ret += "; slt $v0, $t8, $%s;" %(self.allocReg[var2])
            reg = '$v0'
        elif op == '<=':
            if re.search('^[0-9]+$', var1):
                ret += "; li $t8, %s;" %(var1)

                if re.search('^[0-9]+$', var2):
                    ret += "; li $t9, %s; sle $v0, $t8, $t9;" %(var2)
                else:
                    if re.match('^\$', var2):
                        ret += "; sle $v0, $t8, %s;" %(var2)
                    else:
                        ret += "; sle $v0, $t8, $%s;" %(self.allocReg[var2])
            else:
                if re.match('^\$', var1):
                    ret += "; ori $t8, %s, 0;" %(var1)
                else:
                    ret += "; ori $t8, $%s 0;" %(self.allocReg[var1])

                if re.search('^[0-9]+$', var2):
                    ret += "; li $t9, %s; sle $v0, $t8, $t9;" %(var2)
                else:
                    if re.match('^\$', var2):
                        ret += "; sle $v0, $t8, %s;" %(var2)
                    else:
                        ret += "; sle $v0, $t8, $%s;" %(self.allocReg[var2])
            reg = '$v0'
        elif op == '>':
            if re.search('^[0-9]+$', var1):
                ret += "; li $t8, %s;" %(var1)

                if re.search('^[0-9]+$', var2):
                    ret += "; li $t9, %s; sgt $v0, $t8, $t9;" %(var2)
                else:
                    if re.match('^\$', var2):
                        ret += "; sgt $v0, %s, $t8;" %(var2)
                    else:
                        ret += "; sgt $v0, $t8, $%s;" %(self.allocReg[var2])
            else:
                if re.match('^\$', var1):
                    ret += "; ori $t8, %s, 0;" %(var1)
                else:
                    ret += "; ori $t8, $%s 0;" %(self.allocReg[var1])

                if re.search('^[0-9]+$', var2):
                    ret += "; li $t9, %s; sgt $v0, $t8, $t9;" %(var2)
                else:
                    if re.match('^\$', var2):
                        ret += "; sgt $v0, %s, $t8;" %(var2)
                    else:
                        ret += "; sgt $v0, $t8, $%s;" %(self.allocReg[var2])
            reg = '$v0'
        elif op == '>=':
            if re.search('^[0-9]+$', var1):
                ret += "; li $t8, %s;" %(var1)

                if re.search('^[0-9]+$', var2):
                    ret += "; li $t9, %s; sge $v0, $t8, $t9;" %(var2)
                else:
                    if re.match('^\$', var2):
                        ret += "; sge $v0, $t8, %s;" %(var2)
                    else:
                        ret += "; sge $v0, $t8, $%s;" %(self.allocReg[var2])
            else:
                if re.match('^\$', var1):
                    ret += "; ori $t8, %s, 0;" %(var1)
                else:
                    ret += "; ori $t8, $%s 0;" %(self.allocReg[var1])

                if re.search('^[0-9]+$', var2):
                    ret += "; li $t9, %s; sge $v0, $t8, $t9;" %(var2)
                else:
                    if re.match('^\$', var2):
                        ret += "; sge $v0, $t8, %s;" %(var2)
                    else:
                        ret += "; sge $v0, $t8, $%s;" %(self.allocReg[var2])
            reg = '$v0'
        return ret, reg

    ## Deprecated ##
    def getHeap(self):
        ## Have to put the size in $a0 prior to this function call ##
        return '; ; ## Allocating heap using sbrk system call ##;   li $v0, 9;   syscall; ## End of sbrk system call ##;'

    ## Deprecated ##
    def evaluateExpression(self, list):
        res = ''
        reg = ''
        print "[CGen:evaluateExpression] List ", list
        if len(list) > 1 and list[1] == '=':
            # if list[2] != 'new':
            defn = list[0]
            temp = list[2:]
            tmp, temp1 = self.evaluateExpression(temp)
            if tmp:
                res += tmp
            if temp1:
                res +='; ori $%s, %s, 0; ' %(self.allocReg[defn], temp1)
                reg = temp1
        elif list[0] == 'input':
            res = self.inputInt()
            reg = '$v0'
        elif re.match('UNARY ', list[0]):
            if list[1] == '!':
                var = list[2]
                if re.search('^[0-9]+$', var):
                    res = '; li $t8, %s;' %(var)
                    res += '; seq $t9, $t8, $zero;'
                else:
                    res = '; ori $t8, $%s, 0;' %(self.allocReg[var])
                    res += '; seq $t9, $t8, $zero;'
            elif list[1] == '-':
                var = list[2]
                if re.search('^[0-9]+$', var):
                    res = '; li $t8, %s;' %(var)
                    res += '; sub $t9, $zero, $t8;'
                else:
                    res = '; ori $t8, $%s, 0;' %(self.allocReg[var])
                    res += '; sub $t9, $zero, $t8;'
            ## Handle Pre and Post ++/-- ##

            ## Post Operations ##
            elif list[2] == '--':
                # print 'To be implemented.!'
                var = list[1]
                res = '; li $t9, 1; sub $t8, $%s, $t9; ori $t9, $%s, 0;  ori $%s, $t8, 0;' %(self.allocReg[var],self.allocReg[var],self.allocReg[var])
            elif list[2] == '++':
                # print 'To be implemented.!'
                var = list[1]
                res = '; li $t9, 1; add $t8, $%s, $t9; ori $t9, $%s, 0;  ori $%s, $t8, 0;' %(self.allocReg[var],self.allocReg[var],self.allocReg[var])

            ## Pre Operations ##
            elif list[1] == '--':
                # print 'To be implemented.!'
                var = list[2]
                res = '; li $t8, 1; sub $t9, $%s, $t8; ori $%s, $t9, 0;' %(self.allocReg[var],self.allocReg[var])
            elif list[1] == '++':
                # print 'To be implemented.!'
                var = list[2]
                res = '; li $t8, 1; add $t9, $%s, $t8; ori $%s, $t9, 0;' %(self.allocReg[var],self.allocReg[var])
            reg = '$t9'
        elif re.match('BINARY ', list[0]):
            opers = []
            operands = []
            counter = 0
            for x in list:
                if 'UNARY ' in x:
                    tmp1, tmpreg = self.evaluateExpression([x])
                    res += tmp1
                    reg = tmpreg
                    operands.append(reg)
                    counter += 1
                elif 'BINARY ' in x:
                    opers.append(x[7:])
                    counter = 0
                else:
                    operands.append(x)
                    counter+=1

                if len(operands) >= 2 and len(opers) > 0 and counter == 2:
                    x1 = operands.pop()
                    x2 = operands.pop()
                    oper = opers.pop()
                    binexp, reg = self.evalBinExp(x2,x1,oper)
                    res += binexp
                    if reg == '$LO':
                        reg = '$a0'
                        res += '; mflo $a0;'
                    elif reg == '$HO':
                        reg = '$a0'
                        res += '; mfhi $a0;'
                    operands.append(reg)
                    counter -= 1

            ## Once For Loop is exhausted ##
            if len(oper) > 0 and len(operands)>1:
                x1 = operands.pop()
                x2 = operands.pop()
                oper = opers.pop()
                binexp, reg = self.evalBinExp(x2,x1,oper)
                res += binexp
                operands.append(reg)
        elif list[0] == 'print':
            length = len(list)
            exp = list[2:length-2]
            binexp, reg = self.evaluateExpression(exp)
            res += binexp
        else:
            ## Simple Variable or a Number##
            if re.search('^[0-9]+$', list[0]):
                res += '; li $t8, %s; ' %list[0]
                reg = '$t8'
            else:
                if '[' not in list and ']' not in list:
                    reg = '$'+self.allocReg[list[0]]
                else:
                    ## Array Reading ##
                    lbCount = list.count('[')
                    rbCount = list.count(']')
                    if lbCount != rbCount:
                        print "Square brackets are not balanced.!"
                        sys.exit(-1)
                    idx  = 0
                    for i in range(lbCount):
                        newidx1 = list.index('[', idx)
                        newidx2 = list.index(']', newidx1)
                        idx = newidx2
                        binexp, reg = self.evaluateExpression(list[newidx1+1:newidx2])
                        res += binexp
                        if reg != '$t9':
                            res+= ' li $t9, 4; mult %s, $t9;' %(reg)
                        else:
                            res+= ' li $t8, 4; mult %s, $t8;' %(reg)
                        if lbCount > 1 and i != 0:
                            ## Need to add size as an offset as well ##
                            ## Eg: a[i][j] = a + i*4 + i*secDimSize + j*4 ##
                            res += ' ori $t9, $t8, 0; mflo $t8; add $t8, $t9, $t8;'
                        else:
                            res += ' mflo $t8;'
                    res += ' add $t9, $t8, $%s;' %(self.allocReg[list[0]])
                    reg = '$t9'
        return res, reg

    def getIfLabel(self):
        return self.ifLabelStack.pop()

    def getLoopLabel(self):
        return self.loopLabelStack.pop()

    def getLoop2Label(self):
        return self.loop2LabelStack.pop()

    def generateIntermediateCode(self):
        # print self.stmt
        # print
        # print
        for line in self.stmt:
            if 'variable_' in line:
                list = re.split(' ', line)
                if 'variable_' in list[1]:
                    varList = re.sub('variable_', '', list[1])
                    var = re.sub(',', '', varList)
                    reg = self.allocReg[var]
                    line = re.sub('variable_'+var, '$'+reg, line)
                    line = str('  '+line)
                    # print line
                elif 'variable_' in list[2]:
                    varList = re.sub('variable_', '', list[2])
                    var = re.sub(',', '', varList)
                    reg = self.allocReg[var]
                    line = re.sub('variable_'+var, '$'+reg, line)
                    line = str('  '+line)
                    # print line

            ## IF - ELSE Block Handling ##
            elif line == 'BRANCH LABEL_IF_ELSE' or line == 'BRANCH LABEL_IF':
                label = self.genLabel()
                self.ifLabelStack.append(label)
                continue
            elif '__IF_LABEL__' in line and line != 'b __IF_LABEL__':
                label = self.ifLabelStack[-1]
                line = re.sub('__IF_LABEL__', label, line)
                line = str('  '+line)
            elif line == 'b __IF_LABEL__':
                ## This is taken care in ELSE ##
                continue
            elif line == 'BRANCH LABEL_ELSE':
                label = self.genLabel()
                line = str('  b '+label+';'+self.getIfLabel()+':'+';')
                self.ifLabelStack.append(label)
            elif line == 'BRANCH LABEL_IF_ELSE_END' or line == 'BRANCH LABEL_IF_END':
                ## Just Pops the top most label ##
                line = ';%s:;' %self.getIfLabel()

            ## For Loops Handling ##
            elif line == 'BRANCH LABEL_FOR':
                line = str(';## For Loop ##; ')
                label = self.genLabel()
                self.loopLabelStack.append(label)
                label2 = self.genLabel()
                self.loop2LabelStack.append(label2)
                # line += str(';%s:;' %label)
            elif '__FOR_LABEL__' in line:
                label = self.loop2LabelStack[-1]
                line = re.sub('__FOR_LABEL__', label, line)
                line = str('  '+line)
            elif line ==  '__FOR_LABEL_START__':
                line = str(';%s:;' %(self.loopLabelStack[-1]))
            elif line == 'b __FOR_LABEL_START__':
                ## This is handled in FOR_END ##
                continue
            elif line == 'BRANCH LABEL_FOR_END':
                line = str(';  b %s' %self.getLoopLabel())
                line += str(';## End of For LOOP ##;')
                line += str(';%s:;' %self.getLoop2Label())

            ## While Loop Handling ##
            elif line == 'BRANCH LABEL_WHILE':
                line = str(';## While Loop ##; ')
                label = self.genLabel()
                self.loopLabelStack.append(label)
                label2 = self.genLabel()
                self.loop2LabelStack.append(label2)
                line += str(';%s:;' %label)
            elif '__WHILE_LABEL__' in line:
                label = self.loop2LabelStack[-1]
                line = re.sub('__WHILE_LABEL__', label, line)
                line = str('  '+line)
            elif line ==  '__WHILE_LABEL_START__' or line == 'b __WHILE_LABEL_START__':
                ## This is handled in WHILE_END ##
                continue
            elif line == 'BRANCH LABEL_WHILE_END':
                line = str(';  b %s' %self.getLoopLabel())
                line += str(';## End of While LOOP ##;')
                line += str(';%s:;' %self.getLoop2Label())

            ## Do-while Loop Handling ##
            elif line == 'BRANCH LABEL_DO_WHILE':
                line = str(';## Do-while Loop ##; ')
                label = self.genLabel()
                self.loopLabelStack.append(label)
                line += str(';%s:;' %label)
            elif '__DO_WHILE_LABEL__' in line:
                label = self.loopLabelStack.pop()
                line = re.sub('__DO_WHILE_LABEL__', label, line)
                line = str('  '+line)
            elif line ==  '__DO_WHILE_LABEL_START__' or line == 'b __DO_WHILE_LABEL_START__':
                ## This is handled in DO_WHILE_END ##
                continue
            elif line == 'BRANCH LABEL_DO_WHILE_END':
                line = str(';## End of Do-while LOOP ##;')
            elif line == 'BLOCK_START' or line == 'BLOCK_END' or\
               line == 'UNARY START' or line == 'UNARY END' or \
               line == 'BINARY START' or line == 'BINARY END' or \
               line == 'PRINT_START' or line == 'PRINT_END' or \
               line == 'FUNCTION_BLOCK':
                continue
            elif line == 'FUNCTION_BLOCK_END':
               line = ';'
            else:
                if ':' not in line and '#' not in line:
                    line = str('  '+line)

            self.ic.append(line)
        # print self.ic
        # sys.exit(-1)

    def generateASM(self):
        self.generateHeaders()
        for i in self.ic:
            for line in i:
                ## If Label has spaces, code doesnt work, so removing leading spaces ##
                newLine = re.sub(r';\s+LABEL',';LABEL', line)
                self.asmfid.write(re.sub(';', '\n', newLine))
            self.asmfid.write('\n')
        self.asmfid.write(re.sub(';', '\n', self.getExit()))
        ## Closing the opened file descriptors. ##
        self.asmfid.close()
