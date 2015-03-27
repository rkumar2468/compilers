##########################################################################################################
## Class: CodeGen											##
## This class is responsible to generate the final code (XXX.asm) file 					##
## 													##
##													##
## Name: 	Rajendra Kumar Raghupatruni		    						##
## SBU Net ID: 	rraghuaptrun				    						##
## SBU ID: 	109785402				    						##
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

    def generateIntermediateCode(self):
        memcount = 0
        memory = {}
        for key in self.Dict.keys():
            # print self.Dict[key]
            val = self.Dict[key]
            lis = []
            if 'print' not in val and 'memory' not in val:
                defn = val[0]
                temp = val[2:]
                length = len(temp)
                if length == 3:
                    # input or x + y
                    if temp[0] == 'input':
                        lis.append(self.inputInt())
                        if defn not in self.unusedVar:
                            lis.append(' ori $%s, $v0, 0;' %(self.allocReg[defn]))
                    else:
                        # x + y
                        if temp[1] == '+':
                            if re.search('^[0-9]+$', temp[0]):
                                lis.append(" li $t8, %s;" %(temp[0]))
                                if re.search('^[0-9]+$', temp[2]):
                                    lis.append(" li $t9, %s;" %(temp[2]))
                                    lis.append(" add $%s, $t8, $t9;" %(self.allocReg[defn]))
                                else:
                                    lis.append(" add $%s, $t8, $%s;" %(self.allocReg[defn], self.allocReg[temp[2]]))
                            else:
                                if re.search('^[0-9]+$', temp[2]):
                                    lis.append(" li $t8, %s;" %(temp[2]))
                                    lis.append(" add $%s, $t8, $%s;" %(self.allocReg[defn],self.allocReg[temp[0]]))
                                else:
                                    lis.append(" add $%s, $%s, $%s;" %(self.allocReg[defn], self.allocReg[temp[0]],self.allocReg[temp[2]]))

                        elif temp[1] == '-':
                            if re.search('^[0-9]+$', temp[0]):
                                lis.append("li $t8, %s;" %(temp[0]))
                                if re.search('^[0-9]+$', temp[2]):
                                    lis.append(" li $t9, %s;" %(temp[2]))
                                    lis.append(" sub $%s, $t8, $t9;" %(self.allocReg[defn]))
                                else:
                                    lis.append(" sub $%s, $t8, $%s;" %(self.allocReg[defn], self.allocReg[temp[2]]))
                            else:
                                if re.search('^[0-9]+$', temp[2]):
                                    lis.append(" li $t8, %s;" %(temp[2]))
                                    lis.append(" sub $%s, $%s, $t8;" %(self.allocReg[defn],self.allocReg[temp[0]]))
                                else:
                                    lis.append(" sub $%s, $%s, $%s;" %(self.allocReg[defn], self.allocReg[temp[0]],self.allocReg[temp[2]]))

                        elif temp[1] == '*':
                            if re.search('^[0-9]+$', temp[0]):
                                lis.append(" li $t8, %s;" %(temp[0]))
                                if re.search('^[0-9]+$', temp[2]):
                                    lis.append(" li $t9, %s;" %(temp[2]))
                                    lis.append(" mult $t8, $t9;")
                                else:
                                    lis.append(" mult, $t8, $%s;" %(self.allocReg[temp[2]]))
                            else:
                                if re.search('^[0-9]+$', temp[2]):
                                    lis.append(" li $t8, %s;" %(temp[2]))
                                    lis.append(" mult $%s, $t8;" %(self.allocReg[temp[0]]))
                                else:
                                    lis.append(" mult $%s, $%s;" %(self.allocReg[temp[0]],self.allocReg[temp[2]]))
                            lis.append(" mflo $%s;"  %(self.allocReg[defn]))

                        elif temp[1] == '/':
                            if re.search('^[0-9]+$', temp[0]):
                                lis.append(" li $t8, %s;" %(temp[0]))
                                if re.search('^[0-9]+$', temp[2]):
                                    lis.append(" li $t9, %s;" %(temp[2]))
                                    lis.append(" div $t8, $t9;")
                                else:
                                    lis.append(" div, $t8, $%s;" %(self.allocReg[temp[2]]))
                            else:
                                if re.search('^[0-9]+$', temp[2]):
                                    lis.append(" li $t8, %s;" %(temp[2]))
                                    lis.append(" div $%s, $t8;" %(self.allocReg[temp[0]]))
                                else:
                                    lis.append(" div $%s, $%s;" %(self.allocReg[temp[0]],self.allocReg[temp[2]]))
                            lis.append(" mflo $%s;" %(self.allocReg[defn]))

                        elif temp[1] == '%':
                            if re.search('^[0-9]+$', temp[0]):
                                lis.append(" li $t8, %s;" %(temp[0]))
                                if re.search('^[0-9]+$', temp[2]):
                                    lis.append(" li $t9, %s;" %(temp[2]))
                                    lis.append(" div $t8, $t9;")
                                else:
                                    lis.append(" div, $t8, $%s;" %(self.allocReg[temp[2]]))
                            else:
                                if re.search('^[0-9]+$', temp[2]):
                                    lis.append(" li $t8, %s;" %(temp[2]))
                                    lis.append(" div $%s, $t8;" %(self.allocReg[temp[0]]))
                                else:
                                    lis.append(" div $%s, $%s;" %(self.allocReg[temp[0]],self.allocReg[temp[2]]))
                            lis.append(" mfhi $%s;" %(self.allocReg[defn]))

                elif length == 1:
                    # x or 1
                    # print temp
                    if re.search('^[0-9]+$', temp[0]):
                        lis.append(" li $%s, %s;" %(self.allocReg[defn],temp[0]))
                    else:
                        lis.append(" ori $%s, $%s, 0;" %(self.allocReg[defn],self.allocReg[temp[0]]))
                
            elif 'memory' not in val:
                temp = val[2:-1]
                length = len(temp)
                if length == 3:
                    if temp[1] == '+':
                        # add
                        if re.search('^[0-9]+$', temp[0]):
                            lis.append(" li $t8, %s;" %(temp[0]))
                            if re.search('^[0-9]+$', temp[2]):
                                lis.append(" li $t9, %s;" %(temp[2]))
                                lis.append(" add $a0, $t8, $t9;")
                            else:
                                lis.append(" add $a0, $t8, $%s;" %(self.allocReg[temp[2]]))
                        else:
                            if re.search('^[0-9]+$', temp[2]):
                                lis.append(" li $t8, %s;" %(temp[2]))
                                lis.append(" add $a0, $t8, $%s;" %(self.allocReg[temp[0]]))
                            else:
                                lis.append(" add $a0, $%s, $%s;" %(self.allocReg[temp[0]],self.allocReg[temp[2]]))
                        # print  lis
                    elif temp[1] == '-':
                        #     Sub
                        if re.search('^[0-9]+$', temp[0]):
                            lis.append(" li $t8, %s;" %(temp[0]))
                            if re.search('^[0-9]+$', temp[2]):
                                lis.append(" li $t9, %s;" %(temp[2]))
                                lis.append(" sub $a0, $t8, $t9;")
                            else:
                                lis.append(" sub $a0, $t8, $%s;" %(self.allocReg[temp[2]]))
                        else:
                            if re.search('^[0-9]+$', temp[2]):
                                lis.append(" li $t8, %s;" %(temp[2]))
                                lis.append(" sub $a0, $%s, $t8;" %(self.allocReg[temp[0]]))
                            else:
                                lis.append(" sub $a0, $%s, $%s;" %(self.allocReg[temp[0]],self.allocReg[temp[2]]))
                        # print  lis
                        # print ""
                    elif temp[1] == '*':
                        #     Mul
                        if re.search('^[0-9]+$', temp[0]):
                            lis.append(" li $t8, %s;" %(temp[0]))
                            if re.search('^[0-9]+$', temp[2]):
                                lis.append("  li $t9, %s;" %(temp[2]))
                                lis.append(" mult $t8, $t9;")
                            else:
                                lis.append(" mult, $t8, $%s;" %(self.allocReg[temp[2]]))
                        else:
                            if re.search('^[0-9]+$', temp[2]):
                                lis.append(" li $t8, %s;" %(temp[2]))
                                lis.append(" mult $%s, $t8;" %(self.allocReg[temp[0]]))
                            else:
                                lis.append(" mult $%s, $%s;" %(self.allocReg[temp[0]],self.allocReg[temp[2]]))
                        lis.append(" mflo $a0;")

                    elif temp[1] == '/':
                        # Div
                        if re.search('^[0-9]+$', temp[0]):
                            lis.append(" li $t8, %s;" %(temp[0]))
                            if re.search('^[0-9]+$', temp[2]):
                                lis.append(" li $t9, %s;" %(temp[2]))
                                lis.append(" div $t8, $t9;")
                            else:
                                lis.append(" div, $t8, $%s;" %(self.allocReg[temp[2]]))
                        else:
                            if re.search('^[0-9]+$', temp[2]):
                                lis.append(" li $t8, %s;" %(temp[2]))
                                lis.append(" div $%s, $t8;" %(self.allocReg[temp[0]]))
                            else:
                                lis.append(" div $%s, $%s;" %(self.allocReg[temp[0]],self.allocReg[temp[2]]))
                        lis.append(" mflo $a0;")

                    elif temp[1] == '%':
                        # Reminder
                        if re.search('^[0-9]+$', temp[0]):
                            lis.append(" li $t8, %s;" %(temp[0]))
                            if re.search('^[0-9]+$', temp[2]):
                                lis.append(" li $t9, %s;" %(temp[2]))
                                lis.append(" div $t8, $t9;")
                            else:
                                lis.append(" div, $t8, $%s;" %(self.allocReg[temp[2]]))
                        else:
                            if re.search('^[0-9]+$', temp[2]):
                                lis.append(" li $t8, %s;" %(temp[2]))
                                lis.append(" div $%s, $t8;" %(self.allocReg[temp[0]]))
                            else:
                                lis.append(" div $%s, $%s;" %(self.allocReg[temp[0]],self.allocReg[temp[2]]))
                        lis.append(" mfhi $a0;")
                elif length == 1:
                    if re.search('^[0-9]+$', temp[0]):
                        lis.append(" li $a0, %s;" %(temp[0]))
                    else:
                        lis.append((" ori $a0, $%s, 0;") %(self.allocReg[temp[0]]))
                elif length == 0:
                    lis.append(" li $a0, 0;")
                lis.append(self.printInt())
                # print lis
            else:
                if val[0] == 'memory':
                    ## Allocate Memory - 4 Bytes (as it is an integer) ##
                    temp = val[2:]
                    memory[temp[0][:-1]] = memcount
                    lis.append(";## Storing Register Values to Memory ##; la $t8, memory;")
                    lis.append(" sw $%s, %d($t8);;" %(self.allocReg[temp[0]], memory[temp[0][:-1]]))
                    memcount += 4
                elif val[2] == 'memory':
                    temp = val[0:]
                    lis.append(";## Loading Register Values from Memory ##; la $t8, memory;")
                    lis.append(" lw $%s, %d($t8);;" %(self.allocReg[temp[0]], memory[temp[0][:-1]]))
            self.ic.append(lis)
        # print self.ic

    def generateASM(self):
        self.generateHeaders()
        for i in self.ic:
            for line in i:
                self.asmfid.write(re.sub(';', '\n', line))
        self.asmfid.write(re.sub(';', '\n', self.getExit()))
        ## Closing the opened file descriptors. ##
        self.asmfid.close()
