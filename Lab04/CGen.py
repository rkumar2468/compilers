##########################################################################################################
## Class: CodeGen											                                            ##
## This class is responsible to generate the final code (XXX.asm) file 					                ##
## 													                                                    ##
##													                                                    ##
## Name: 	Rajendra Kumar Raghupatruni		    						                                ##
## SBU Net ID: 	rraghuaptrun				    						                                ##
## SBU ID: 	109785402				    						                                        ##
##########################################################################################################

import re

class CodeGen:
    def __init__(self, asmfile, allocReg, Dict, remVar):
        self.get = 10
        self.asmfid = open(asmfile,'w')
        self.allocReg = allocReg
        self.Dict = Dict
        self.ic = []
        self.unusedVar = remVar
        self.labelCount = 0
        self.labelStack = []
        self.ifLabelStack = []
        self.loopLabelStack = []
        self.loop2LabelStack = []

    def genLabel(self):
        ret = 'LABEL%s' %self.labelCount
        self.labelCount += 1
        return ret

    def peekLabel(self, type):
        if type == 'if':
            return self.ifLabelStack[-1]
        elif type == 'while':
            return self.loopLabelStack[-1]

    ## Sbrk system call - To Allocate memory ##
    def allocMem(self, bytes):
        return '; ## Allocating Memory ##; li $a0, %s; li $v0, 9; syscall;;' %(bytes)

    def generateHeaders(self):
        self.asmfid.write(" .globl main\n")
        self.asmfid.write("\n .data\n str4: .asciiz \"\\n\" \n memory: .word 0 1 2 3 4\n")
        self.asmfid.write("\n .text\n")
        self.asmfid.write("main:\n")

    def getExit(self):
        return '; ## Exit ##; la $a0, str4; li $v0, 4; syscall;; li $v0, 10; syscall;;'

    def inputInt(self):
        return ';## Reading input from stdin ##; li $v0, 5; syscall;;'

    def printInt(self):
        return '; ## Adding New Line ##; ori $t8, $a0, 0; la $a0, str4; li $v0, 4; syscall;; ## Printing Integer ##; ori $a0, $t8, 0; li $v0, 1; syscall;;'

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

    def evaluateExpression(self, list):
        res = ''
        reg = ''
        print "[CGen:evaluateExpression] List ", list
        if list[0] == 'input':
            res = self.inputInt()
            reg = '$v0'
        elif re.match('UNARY ', list[0]):
            if list[0][6] == '!':
                var = list[0][7:]
                if re.search('^[0-9]+$', var):
                    res = '; li $t8, %s;' %(var)
                    res += '; seq $t9, $t8, $zero;'
                else:
                    res = '; ori $t8, $%s, 0;' %(self.allocReg[var])
                    res += '; seq $t9, $t8, $zero;'

            elif list[0][6] == '-':
                var = list[0][7:]
                if re.search('^[0-9]+$', var):
                    res = '; li $t8, %s;' %(var)
                    res += '; sub $t9, $zero, $t8;'
                else:
                    res = '; ori $t8, $%s, 0;' %(self.allocReg[var])
                    res += '; sub $t9, $zero, $t8;'
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
                reg = '$'+self.allocReg[list[0]]
        return res, reg

    def getIfLabel(self):
        return self.ifLabelStack.pop()

    def getLoopLabel(self):
        return self.loopLabelStack.pop()

    def getLoop2Label(self):
        return self.loop2LabelStack.pop()

    def generateIntermediateCode(self):
        memcount = 0
        memory = {}
        for key in self.Dict.keys():
            lis = []
            # print "Raa -- ", key, self.Dict[key]
            val = self.Dict[key]
            if len(val) <= 0:
                continue
            if 'memory' not in val:
                if len(val) > 1 and val[1] == '=':
                    defn = val[0]
                    temp = val[2:]
                    ret, reg = self.evaluateExpression(temp)
                    if ret:
                        lis.append(ret)
                        lis.append('; ori $%s, %s, 0; ' %(self.allocReg[defn], reg))
                elif val[0] == 'print':
                    ret, reg = self.evaluateExpression(val)
                    if ret:
                        lis.append(ret)
                    if reg:
                        if reg not in ['$HI', '$LO']:
                            lis.append('; ori $a0, %s, 0; ' %(reg))
                        else:
                            if reg == '$LO':
                                lis.append('; mflo $a0;')
                            else:
                                lis.append('; mfhi $a0;')
                        lis.append('; ori $t8, $a0, 0;')
                        lis.append(self.printInt())

                elif val[0] == 'if':
                    label = self.genLabel()
                    self.ifLabelStack.append(label)

                    ret, reg = self.evaluateExpression(val[1:])
                    if ret:
                        lis.append(ret)
                        if reg not in ['$HI', '$LO']:
                            ## Branch based on reg ##
                            lis.append('; beq %s, $zero, %s; ' %(reg, label))
                        else:
                            if reg == '$LO':
                                lis.append('; mflo $t8;')
                                lis.append('; beq $t8, $zero, %s; ' %label)
                            else:
                                lis.append('; mfhi $t8;')
                                lis.append('; beq $t8, $zero, %s; ' %label)
                    elif reg:
                        if reg not in ['$HI', '$LO']:
                            ## Just Branch ##
                            lis.append('; blez %s, %s; ' %(reg, label))
                        else:
                            if reg == '$LO':
                                lis.append('; mflo $t8;')
                                lis.append('; blez $t8, %s; ' %label)
                            else:
                                lis.append('; mfhi $t8;')
                                lis.append('; blez $t8, %s; ' %label)
                elif val[0] == 'if_end' or val[0] == 'if_else_end':
                    lis.append(';%s:;' %self.getIfLabel())
                elif val[0] == 'else':
                    label = self.genLabel()
                    lis.append('; beq $zero, $zero, %s; ' %(label))
                    lis.append(';%s:;' %self.getIfLabel())
                    self.ifLabelStack.append(label)
                elif val[0] == 'LOOP':
                    label = self.genLabel()
                    self.loopLabelStack.append(label)
                    label2 = self.genLabel()
                    self.loop2LabelStack.append(label2)
                    lis.append(';%s:;' %label)
                    ret, reg = self.evaluateExpression(val[1:])
                    if ret:
                        lis.append(ret)
                    if reg:
                        if reg not in ['$HI', '$LO']:
                            lis.append('; beq %s, $zero, %s; ' %(reg, label2))
                        else:
                            if reg == '$LO':
                                lis.append('; mflo $t8;')
                                lis.append('; beq $t8, $zero, %s; ' %label2)
                            else:
                                lis.append('; mfhi $t8;')
                                lis.append('; beq $t8, $zero, %s; ' %label2)

                elif val[0] == 'END_LOOP':
                    lis.append('; beq $zero, $zero, %s' %self.getLoopLabel())
                    lis.append(';%s:;' %self.getLoop2Label())
            else:
                ## It is either X = memory or memory = x ##
                if val[0] == 'memory':
                    ## Allocate Memory - 4 Bytes (as it is an integer) ##
                    temp = val[2:]
                    memory[temp[0][:-1]] = memcount
                    lis.append(";## Storing Register Values to Memory ##; la $t8, memory;")
                    lis.append(" sw $%s, %d($t8);" %(self.allocReg[temp[0]], memory[temp[0][:-1]]))
                    memcount += 4
                elif val[2] == 'memory':
                    temp = val[0:]
                    lis.append(";## Loading Register Values from Memory ##; la $t8, memory;")
                    lis.append(" lw $%s, %d($t8);" %(self.allocReg[temp[0]], memory[temp[0][:-1]]))

            ## Appending to main list ##
            self.ic.append(lis)
        for line in self.ic:
            print line

    def generateASM(self):
        self.generateHeaders()
        for i in self.ic:
            for line in i:
                ## If Label has spaces, code doesnt work, so removing leading spaces ##
                newLine = re.sub(r';\s+LABEL',';LABEL', line)
                self.asmfid.write(re.sub(';', '\n', newLine))
        self.asmfid.write(re.sub(';', '\n', self.getExit()))
        ## Closing the opened file descriptors. ##
        self.asmfid.close()
