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
                    ret += "; ori $t8, %s, $zero;" %(var1)
                else:
                    ret += "; ori $t8, $%s, $zero;" %(self.allocReg[var1])
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
                    ret += "; ori $t8, %s, $zero;" %(var1)
                else:
                    ret += "; ori $t8, $%s, $zero;" %(self.allocReg[var1])
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
                    ret += "; ori $t8, %s, $zero;" %(var1)
                else:
                    ret += "; ori $t8, $%s, $zero;" %(self.allocReg[var1])
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
                    ret += "; ori $t8, %s, $zero;" %(var1)
                else:
                    ret += "; ori $t8, $%s, $zero;" %(self.allocReg[var1])
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
                ret += '; sgt $t9, $t8, $zero; bgtz $t8, LABEL%s;' %(self.labelCount)
                self.labelStack.append('LABEL%s:;' %self.labelCount)
                self.labelCount += 1

                if re.search('^[0-9]+$', var2):
                    ret += "; li $t8, %s; sgt $t9, $t8, $zero;;" %(var2)
                else:
                    if re.match('^\$', var2):
                        ret += "; sgt $t9, %s, $zero;;" %(var2)
                    else:
                        ret += "; sgt $t9, $%s, $zero;;" %(self.allocReg[var2])
                ret += self.labelStack.pop()

            else:
                if re.match('^\$', var1):
                    ret += "; ori $t8, %s, $zero;" %(var1)
                else:
                    ret += "; ori $t8, $%s, $zero;" %(self.allocReg[var1])
                ret += '; sgt $t9, $t8, $zero; bgtz $t8, LABEL%s' %self.labelCount
                self.labelStack.append('LABEL%s:;' %self.labelCount)
                self.labelCount += 1

                if re.search('^[0-9]+$', var2):
                    ret += "; li $t8, %s; sgt $t9, $t8, $zero;;" %(var2)
                else:
                    if re.match('^\$', var2):
                        ret += "; sgt $t9, %s, $zero;;" %(var2)
                    else:
                        ret += "; sgt $t9, $%s, $zero;;" %(self.allocReg[var2])
                ret += self.labelStack.pop()
            reg = '$t9'
        elif op == '&&':
            if re.search('^[0-9]+$', var1):
                ret += "; li $t8, %s;" %(var1)
                ret += '; sgt $t9, $t8, $zero; blez $t8, LABEL%s' %self.labelCount
                self.labelStack.append('LABEL%s:;' %self.labelCount)
                self.labelCount += 1

                if re.search('^[0-9]+$', var2):
                    ret += "; li $t8, %s; sgt $t9, $t8, $zero;;" %(var2)
                else:
                    if re.match('^\$', var2):
                        ret += "; sgt $t9, %s, $zero;;" %(var2)
                    else:
                        ret += "; sgt $t9, $%s, $zero;;" %(self.allocReg[var2])
                ret += self.labelStack.pop()

            else:
                if re.match('^\$', var1):
                    ret += "; ori $t8, %s, $zero;" %(var1)
                else:
                    ret += "; ori $t8, $%s, $zero;" %(self.allocReg[var1])
                ret += '; sgt $t9, $t8, $zero; blez $t8, LABEL%s' %self.labelCount
                self.labelStack.append('LABEL%s:;' %self.labelCount)
                self.labelCount += 1

                if re.search('^[0-9]+$', var2):
                    ret += "; li $t8, %s; sgt $t9, $t8, $zero;;" %(var2)
                else:
                    if re.match('^\$', var2):
                        ret += "; sgt $t9, %s, $zero;;" %(var2)
                    else:
                        ret += "; sgt $t9, $%s, $zero;;" %(self.allocReg[var2])

                ret += self.labelStack.pop()
            reg = '$t9'

        elif op == '==':
            if re.search('^[0-9]+$', var1):
                ret += "; li $t8, %s;" %(var1)

                if re.search('^[0-9]+$', var2):
                    ret += "; li $t9, %s; seq $v0, $t9, $t8;;" %(var2)
                else:
                    if re.match('^\$', var2):
                        ret += "; seq $v0, %s, $t8;;" %(var2)
                    else:
                        ret += "; seq $v0, $%s, $t8;;" %(self.allocReg[var2])

            else:
                if re.match('^\$', var1):
                    ret += "; ori $t8, %s, $zero;" %(var1)
                else:
                    ret += "; ori $t8, $%s $zero;" %(self.allocReg[var1])

                if re.search('^[0-9]+$', var2):
                    ret += "; li $t9, %s; seq $v0, $t9, $t8;;" %(var2)
                else:
                    if re.match('^\$', var2):
                        ret += "; seq $v0, %s, $t8;;" %(var2)
                    else:
                        ret += "; seq $v0, $%s, $t8;;" %(self.allocReg[var2])

            reg = '$v0'

        elif op == '!=':
            if re.search('^[0-9]+$', var1):
                ret += "; li $t8, %s;" %(var1)

                if re.search('^[0-9]+$', var2):
                    ret += "; li $t9, %s; sne $v0, $t9, $t8;;" %(var2)
                else:
                    if re.match('^\$', var2):
                        ret += "; sne $v0, %s, $t8;;" %(var2)
                    else:
                        ret += "; sne $v0, $%s, $t8;;" %(self.allocReg[var2])

            else:
                if re.match('^\$', var1):
                    ret += "; ori $t8, %s, $zero;" %(var1)
                else:
                    ret += "; ori $t8, $%s $zero;" %(self.allocReg[var1])

                if re.search('^[0-9]+$', var2):
                    ret += "; li $t9, %s; sne $v0, $t9, $t8;;" %(var2)
                else:
                    if re.match('^\$', var2):
                        ret += "; sne $v0, %s, $t8;;" %(var2)
                    else:
                        ret += "; sne $v0, $%s, $t8;;" %(self.allocReg[var2])

            reg = '$v0'
        elif op == '<':
            if re.search('^[0-9]+$', var1):
                ret += "; li $t8, %s;" %(var1)

                if re.search('^[0-9]+$', var2):
                    ret += "; li $t9, %s; slt $v0, $t9, $t8;;" %(var2)
                else:
                    if re.match('^\$', var2):
                        ret += "; slt $v0, %s, $t8;;" %(var2)
                    else:
                        ret += "; slt $v0, $%s, $t8;;" %(self.allocReg[var2])
            else:
                if re.match('^\$', var1):
                    ret += "; ori $t8, %s, $zero;" %(var1)
                else:
                    ret += "; ori $t8, $%s $zero;" %(self.allocReg[var1])

                if re.search('^[0-9]+$', var2):
                    ret += "; li $t9, %s; slt $v0, $t9, $t8;;" %(var2)
                else:
                    if re.match('^\$', var2):
                        ret += "; slt $v0, %s, $t8;;" %(var2)
                    else:
                        ret += "; slt $v0, $%s, $t8;;" %(self.allocReg[var2])

            reg = '$v0'
        elif op == '<=':
            if re.search('^[0-9]+$', var1):
                ret += "; li $t8, %s;" %(var1)

                if re.search('^[0-9]+$', var2):
                    ret += "; li $t9, %s; sle $v0, $t9, $t8;;" %(var2)
                else:
                    if re.match('^\$', var2):
                        ret += "; sle $v0, %s, $t8;;" %(var2)
                    else:
                        ret += "; sle $v0, $%s, $t8;;" %(self.allocReg[var2])

            else:
                if re.match('^\$', var1):
                    ret += "; ori $t8, %s, $zero;" %(var1)
                else:
                    ret += "; ori $t8, $%s $zero;" %(self.allocReg[var1])

                if re.search('^[0-9]+$', var2):
                    ret += "; li $t9, %s; sle $v0, $t9, $t8;;" %(var2)
                else:
                    if re.match('^\$', var2):
                        ret += "; sle $v0, %s, $t8;;" %(var2)
                    else:
                        ret += "; sle $v0, $%s, $t8;;" %(self.allocReg[var2])
            reg = '$v0'
        elif op == '>':
            if re.search('^[0-9]+$', var1):
                ret += "; li $t8, %s;" %(var1)

                if re.search('^[0-9]+$', var2):
                    ret += "; li $t9, %s; sgt $v0, $t9, $t8;;" %(var2)
                else:
                    if re.match('^\$', var2):
                        ret += "; sgt $v0, %s, $t8;;" %(var2)
                    else:
                        ret += "; sgt $v0, $%s, $t8;;" %(self.allocReg[var2])

            else:
                if re.match('^\$', var1):
                    ret += "; ori $t8, %s, $zero;" %(var1)
                else:
                    ret += "; ori $t8, $%s $zero;" %(self.allocReg[var1])

                if re.search('^[0-9]+$', var2):
                    ret += "; li $t9, %s; sgt $v0, $t9, $t8;;" %(var2)
                else:
                    if re.match('^\$', var2):
                        ret += "; sgt $v0, %s, $t8;;" %(var2)
                    else:
                        ret += "; sgt $v0, $%s, $t8;;" %(self.allocReg[var2])

            reg = '$v0'
        elif op == '>=':
            if re.search('^[0-9]+$', var1):
                ret += "; li $t8, %s;" %(var1)

                if re.search('^[0-9]+$', var2):
                    ret += "; li $t9, %s; sge $v0, $t9, $t8;;" %(var2)
                else:
                    if re.match('^\$', var2):
                        ret += "; sge $v0, %s, $t8;;" %(var2)
                    else:
                        ret += "; sge $v0, $%s, $t8;;" %(self.allocReg[var2])

            else:
                if re.match('^\$', var1):
                    ret += "; ori $t8, %s, $zero;" %(var1)
                else:
                    ret += "; ori $t8, $%s $zero;" %(self.allocReg[var1])

                if re.search('^[0-9]+$', var2):
                    ret += "; li $t9, %s; sge $v0, $t9, $t8;;" %(var2)
                else:
                    if re.match('^\$', var2):
                        ret += "; sge $v0, %s, $t8;;" %(var2)
                    else:
                        ret += "; sge $v0, $%s, $t8;;" %(self.allocReg[var2])
            reg = '$v0'

        return ret, reg

    def evaluateExpression(self, list):
        res = ''
        reg = ''
        print list
        if list[0] == 'input':
            res = self.inputInt()
            reg = '$v0'
        elif re.match('UNARY ', list[0]):
            if list[0][6] == '!':
                var = list[0][7:]
                if re.search('^[0-9]+$', var):
                    res = '; li $t8, $%s;' %(var)
                    res += '; seq $t9, $t8, $zero;'
                else:
                    res = '; ori $t8, $%s, 0;' %(self.allocReg[var])
                    res += '; seq $t9, $t8, $zero;'

            elif list[0][6] == '-':
                var = list[0][7:]
                if re.search('^[0-9]+$', var):
                    res = '; li $t8, $%s;' %(var)
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
            if length > 4:
                exp = list[2:length-2]
            else:
                exp = list[2:length-1]
            binexp, reg = self.evaluateExpression(exp)
            res += binexp
        elif re.match('print ', list[0]):
            x = 10
        elif re.match('print ', list[0]):
            x = 10

        return res, reg

    def generateIntermediateCode(self):
        for key in self.Dict.keys():
            lis = []
            # print key, self.Dict[key]
            val = self.Dict[key]
            if len(val) > 1 and val[1] == '=':
                defn = val[0]
                temp = val[2:]
                ret, reg = self.evaluateExpression(temp)
                if ret:
                    lis.append(ret)
                    lis.append('; ori $%s, %s, $zero;; ' %(self.allocReg[defn], reg))
            elif val[0] == 'print':
                # print " hi raj ", val
                ret, reg = self.evaluateExpression(val)
                if ret:
                    lis.append(ret)
                    lis.append('; ori $a0, %s, $zero;; ' %(reg))
                    lis.append(self.printInt())

            ## Appending to main list ##
            self.ic.append(lis)
        # for line in self.ic:
        #     print line

    def generateASM(self):
        self.generateHeaders()
        for i in self.ic:
            for line in i:
                self.asmfid.write(re.sub(';', '\n', line))
        self.asmfid.write(re.sub(';', '\n', self.getExit()))
        ## Closing the opened file descriptors. ##
        self.asmfid.close()
