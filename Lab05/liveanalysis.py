##########################################################################################################
## Class: LiveAnalysis											                                        ##
## This class is responsible to allocate registers to the variables of the proto file			        ##
## run () is a wrapper which checks for the register allocation 					                    ##
##													                                                    ##
## Name: 	    Rajendra Kumar Raghupatruni		    						                            ##
## SBU Net ID: 	rraghuaptrun				    						                                ##
## SBU ID: 	    109785402				    						                                    ##
##########################################################################################################

import re, sets, copy, sys

# Live analysis #
class LiveAnalysis:
    def __init__(self, stmt):
        self.stmt = stmt
        self.math = ['+','-','*','/','%','&&','||','!', '==', '!=', '<', '>', '<=', '>=']
        self.umath = ['++', '--', '!', '-']
        self.registers = ['t0', 't1', 't2', 't3', 't4', 't5', 't6', 't7']
        self.allocReg = {}
        self.spill = ''
        self.Def = []
        self.Use = []
        self.In = []
        self.Out = []
        self.Eq = '='
        self.Dict = {}
        self.inp = 'input'
        self.useDict = {}
        self.defDict = {}
        self.inDict = {}
        self.outDict = {}
        self.variables = sets.Set([])
        self.lineno = 0
        self.graph = {}
        self.unaryOps = ['-', '!']
        self.types = {}
        self.symbols = ['new', 'int', 'bool', '[', ']']
        self.nonArrayVar = sets.Set([])
        self.memory = {}
        self.memcount = 0

    def removeLinesFromStatement(self, stmt, idx, var):
        countVar = stmt.count(var)
        for cnt in range(countVar):
            newIdx = stmt.index(var,idx)
            idx = newIdx + 1
            if stmt[newIdx-1] != ';' and \
               stmt[newIdx-1] != 'BLOCK_START' and \
               stmt[newIdx-1] != 'BLOCK_END' or \
               stmt[newIdx+2] == 'input':
                continue
            semiIdx = stmt.index(';', newIdx)
            offset = semiIdx - newIdx + 1
            for i in range(offset):
                # print "Removing ", stmt[newIdx]
                stmt.pop(newIdx)
        # print stmt
        return stmt

    def checkIfVarUsed(self, stmt, var):
        idx = 0
        length = len(stmt)
        # while True:
        for i in stmt:
            if 'variable_'+var in i:
                lis = re.split(' ', i)
                # print i, " <--> ", lis[2], " <--> "
                if lis[2] == 'variable_'+var+',':
                    # print "Returning 0 for %s " %var
                    return 0
        return -1

    def removeElementsBasedOnVar(self, stmt, var):
        tempStmt = []
        for i in stmt:
            if 'variable_'+var+',' in i:
                # print "Removing ", i
                continue
            tempStmt.append(i)
        return tempStmt

    def removeUnusedAssignments2(self, stmt):
        print self.nonArrayVar
        print
        print
        for i in self.nonArrayVar:
            # print "Variable Checking ", i, "\n"
            # self.checkIfVarUsed(stmt, i)
            if self.checkIfVarUsed(stmt, i) != 0:
                # print "variable %s not used - so removing " %i
                stmt = self.removeElementsBasedOnVar(stmt, i)
        return stmt

    def removeUnusedAssignments(self, stmt):
        bDict = {}
        block = 0
        donotRemove = []
        for i in self.Dict.keys():
            list = self.Dict[i]
            length = len(list)
            if 'BLOCK_START' in list:
                block += 1
                continue
            elif 'BLOCK_END' in list:
                if block in bDict.keys() and len(bDict[block]) != 0:
                    ## Remove the line ##
                    print "Remove the line."
                    ## Code for removing the line ##
                    ## Go till block no- block ##
                    lis = bDict[block]
                    print lis
                    ## If there are multiple = in the statement dont remove ##
                    idx = 0
                    for i in range(block):
                        newIdx = stmt.index('BLOCK_START',idx)
                        idx = newIdx+1
                        # print idx
                    for i in set(lis):
                        ## From there remove the entries of the assignment ##
                        nstmt = self.removeLinesFromStatement(stmt,idx,i)
                        # print nstmt
                        stmt = nstmt
                block -= 1
                continue
            if list[1] == '=':
                if 'input' in list:
                    if '[' not in list:
                        donotRemove.append(list[0])
                for i in range(length-1):
                    val = list[i+1]
                    if (val != 'input' and \
                        not re.search('^[0-9]+$', val) and \
                        val not in [')', '(', ';', '='] and \
                        val not in self.umath and \
                        val not in self.symbols):
                        if 'UNARY' in val or 'BINARY' in val:
                            continue
                        else:
                            if i+2 < length-1 and list[i+2] == '=':
                                if block in bDict.keys():
                                    bDict[block].append(list[0])
                                else:
                                    lis = [list[0]]
                                    bDict[block] = lis
                            else:
                                lis = bDict[block]
                                if val in lis:
                                    bDict[block] = [x for x in bDict[block] if x != val]
                if block in bDict.keys():
                    bDict[block].append(list[0])
                else:
                    lis = [list[0]]
                    bDict[block] = lis
            elif length > 0 and list[0] == 'print':
                ## Update use variable ##
                for val in list[1:]:
                    if (not re.search('^[0-9]+$', val) and \
                        val not in [')', '(', ';', '='] and \
                        val not in self.umath and \
                        val not in self.symbols):
                        if 'UNARY' in val or 'BINARY' in val:
                           continue
                        else:
                            lis = bDict[block]
                            if val in lis:
                                bDict[block] = [x for x in bDict[block] if x != val]
            else:
                ## Handling If and While ##
                if length > 1:
                    # print list
                    for val in list[1:]:
                        if (not re.search('^[0-9]+$', val) and \
                            val not in [')', '(', ';', '='] and \
                            val not in self.umath and \
                            val not in self.symbols):
                            if 'UNARY' in val or 'BINARY' in val:
                                continue
                            else:
                                lis = bDict[block]
                                if val in lis:
                                    bDict[block] = [x for x in bDict[block] if x != val]
        return stmt

    def semanticsAssignmentCheck(self):
        bDict = {}
        block = 0
        for i in self.Dict.keys():
            list = self.Dict[i]
            length = len(list)
            print ' Raj: ', list
            if length == 0:
                continue
            elif 'BLOCK_START' in list:
                block += 1
                continue
            elif 'BLOCK_END' in list:
                block -= 1
                continue
            elif list[1] == '=':
                if block in bDict.keys():
                    bDict[block].append(list[0])
                else:
                    lis = [list[0]]
                    bDict[block] = lis
                for i in range(length):
                    val = list[length - i - 1]
                    if (val != 'input' and \
                        not re.search('^[0-9]+$', val) and \
                        val not in [')', '(', ';', '='] and \
                        val not in self.umath and \
                        val not in self.symbols):
                        if 'UNARY' in val or 'BINARY' in val:
                            continue
                        else:
                            # print length-i
                            if i>0 and list[length - i] == '=':
                                if block in bDict.keys():
                                    bDict[block].append(val)
                                else:
                                    lis = [val]
                                    bDict[block] = lis
                            if block in bDict.keys() and val not in bDict[block]:
                                print "Static Semantic Failed for the variable: %s \nMSG: Used but not defined." %(val)
                                sys.exit(-1)
            elif length > 0 and list[0] == 'print':
                ## Update use variable ##
                for val in list[1:]:
                    if (not re.search('^[0-9]+$', val) and \
                        val not in [')', '(', ';', '='] and \
                        val not in self.umath and \
                        val not in self.symbols):
                        if 'UNARY' in val or 'BINARY' in val:
                           continue
                        else:
                            if block in bDict.keys() and val not in bDict[block]:
                                print "Static Semantic Failed for the variable: %s \nMSG: Used but not defined." %(val)
                                sys.exit(-1)
            else:
                ## Handling If and While ##
                if length > 1:
                    # print list
                    for val in list[1:]:
                        if (not re.search('^[0-9]+$', val) and \
                            val not in [')', '(', ';', '='] and \
                            val not in self.umath and \
                            val not in self.symbols):
                            if 'UNARY' in val or 'BINARY' in val:
                                continue
                            else:
                                if block in bDict.keys() and val not in bDict[block]:
                                    print "Static Semantic Failed for the variable: %s \nMSG: Used but not defined." %(val)
                                    sys.exit(-1)

    def checkIfVarDeclared(self, var, varList):
        ret = 0
        length = len(varList)
        for i in range(length):
            curr = varList[length - i - 1]
            if var in curr.keys():
                return 1
        return ret

    def removeUnnecessaryItems(self):
        newStmt = []
        # bend = 0
        prev = ''
        declStart = 0
        for x in self.stmt:
            if x == None:
                continue
            if x == 'BLOCK_END':
                # bend = 1
                newStmt.append(x)
                newStmt.append(';')
                continue
            elif declStart == 1:
                if x == ';':
                    declStart = 0
            # elif x != 'BLOCK_START'  and prev != x and declStart == 0:
            elif prev != x and declStart == 0:
                if x == 'BLOCK_START':
                    newStmt.append(x)
                    newStmt.append(';')
                elif 'TYPE' in x:
                    declStart = 1
                else:
                    newStmt.append(x)
                if x == ';':
                    prev = x
                else:
                    prev = ''
                # bend = 0
        return newStmt

    def updateVariableName(self, stmt, pos, variable, dict, stack, varDict):
        offset = pos
        block = 0
        for entry in stmt[pos:]:
            if entry == ',' or entry == '[' or entry == ']':
                offset += 1
                continue
            if entry == 'BLOCK_START':
                block += 1
                offset += 1
                continue
            elif entry == 'BLOCK_END':
                block -= 1
                offset += 1
                continue
            if block == 0:
                if entry == 'BLOCK_END':
                    break
                elif entry == variable:
                    val = dict[entry]
                    if val > 1:
                        ## Have to update even the stack dictionary ##
                        newVar = str(entry) + str(val)
                        poped = stack.pop()
                        if entry in poped.keys():
                            value = poped[entry]
                            poped.pop(entry)
                            poped[newVar] = value
                            stmt[offset] = newVar
                            # varDict[entry] -= 1
                            varDict[newVar] = 1
                        elif newVar in poped.keys():
                            stmt[offset] = newVar
                        else:
                            print "error..!"
                        stack.append(poped)
            offset += 1
        return stmt, stack, varDict

    def staticSemanticCheck(self):
        print 'Intermediate Code: ',self.stmt
        ## Static Semantic Check ##
        type = ''
        start = 1
        blockStart = 1
        declStart = 0
        stack = []
        defStack = []
        stack.append(self.types)
        bcnt = 0
        curr = {}
        variables = {}
        oldStmt = copy.deepcopy(self.stmt)
        pos = 0
        stmt = []
        for x in oldStmt:
            if x in ['PRINT_START', 'PRINT_END', 'BRANCH LABEL_WHILE',
                     'BRANCH LABEL_WHILE_END', 'BRANCH LABEL_DO_WHILE',
                     'BRANCH LABEL_DO_WHILE_END', 'BRANCH LABEL_IF', 'BRANCH LABEL_IF_ELSE',
                     'BRANCH LABEL_ELSE', 'BRANCH LABEL_IF_ELSE_END', 'BRANCH LABEL_IF_END',
                     'BRANCH LABEL_WHILE', 'BRANCH LABEL_WHILE_END','BRANCH LABEL_DO_WHILE',
                     'BRANCH LABEL_DO_WHILE_END', 'BRANCH LABEL_FOR', 'BRANCH LABEL_FOR_END'] or x == None:
                pos += 1
                continue

            if x == ';' and declStart == 1:
                declStart = 0

            if 'TYPE' in x and (blockStart == 1 or start == 1):
                start = 0
                type = x[5:]
                declStart = 1
                pos += 1
                continue
            if 'BLOCK_START' in x:
                if start == 0:
                    newdict = {}
                    stack.append(newdict)
                    new2dict = {}
                    defStack.append(new2dict)
                blockStart = 1
                ## Get the top of the stack ##
                # stack.append(block+bcnt)
                curr = stack[-1]
                # bcnt += 1
            elif 'BLOCK_END' in x:
                blockStart = 0
                if len(stack) > 0:
                    poped = stack.pop()
                    for item in poped:
                        if variables[item] == 1:
                            variables.pop(item)
                        else:
                            variables[item] -= 1

            elif declStart == 1:
                if x != ',' and x != ']' and x != '[':
                    curr[x] = type
                    if x in variables.keys():
                        variables[x] += 1
                    else:
                        variables[x] = 1
                stmt, stack, variables = self.updateVariableName(oldStmt,pos,x,variables, stack, variables)
                # print stmt
            elif x not in ['=', ',', ';', 'input', '(', ')'] and \
                x not in self.math and \
                x not in self.umath and \
                'BINARY' not in x and\
                'UNARY ' not in x and \
                x not in self.symbols and \
                not re.match(r'[0-9]+', x):
                if self.checkIfVarDeclared(x, stack) == 0:
                    print "Error: Variable '%s' used but not declared.! " %(x)
                    sys.exit(-1)

            pos += 1
            # print variables
        print "Static Semantics check succeeded.!"
        # sys.exit(-1)
        self.stmt = stmt
        newStmt = self.removeUnnecessaryItems()
        # print newStmt
        self.stmt = newStmt

    def reset(self):
        self.spill = ''
        self.Def = []
        self.Use = []
        self.In = []
        self.Out = []
        self.Eq = '='
        self.Dict = {}
        self.inp = 'input'
        self.useDict = {}
        self.defDict = {}
        self.inDict = {}
        self.outDict = {}
        self.variables = sets.Set([])
        self.nonArrayVar = sets.Set([])
        self.lineno = 0
        self.graph = {}
        self.allocReg = {}

    def getLAStmt(self):
        return self.stmt

    #  Building Dictionary  #
    def buildDictionary(self):
        i = 0
        appendVal = []
        printSet = 0
        done = 0
        ifLabel = 0
        elseLabel = 0
        whileStart = 0
        forStart = 0
        doWhileEnd = 0
        # flag = 0
        for line in self.stmt:
            if line == None:
                continue
            ## Print Handling ##
            if 'PRINT_START' in line:
                if appendVal:
                    appendVal.append('print')
                else:
                    appendVal=['print']
                appendVal.append('(')
                printSet = 1
                done = 0
                continue
            elif 'PRINT_END' in line:
                appendVal.append(')')
                appendVal.append(';')
                printSet = 0
                if ifLabel == 0 and whileStart == 0 and elseLabel == 0 and forStart == 0:
                    done = 1
                else:
                    continue

            if line == 'BRANCH LABEL_IF' or line == 'BRANCH LABEL_IF_ELSE':
                ifLabel += 1
                # elseLabel = 0
                if appendVal:
                    appendVal.append('if')
                else:
                    appendVal=['if']
                continue
            elif line == 'BRANCH LABEL_ELSE':
                appendVal.append('else')
                elseLabel += 1
                # ifLabel = 0
                continue
            elif line == 'BRANCH LABEL_IF_ELSE_END':
                appendVal.append('if_else_end')
                appendVal.append(';')
                ifLabel -= 1
                elseLabel -= 1
                if ifLabel == 0 and whileStart == 0 and elseLabel == 0 and forStart == 0:
                    done  = 1
                else:
                    continue
            elif line == 'BRANCH LABEL_IF_END':
                appendVal.append('if_end')
                appendVal.append(';')
                ifLabel -= 1
                if ifLabel == 0 and whileStart == 0 and elseLabel == 0 and forStart == 0:
                    done  = 1
                else:
                    continue

            if line == 'BRANCH LABEL_WHILE':
                whileStart += 1
                if appendVal:
                    appendVal.append('LOOP')
                else:
                    appendVal=['LOOP']
                continue
                # appendVal.append('LOOP')
            elif line == 'BRANCH LABEL_WHILE_END':
                appendVal.append('END_LOOP')
                whileStart -= 1
                if ifLabel == 0 and whileStart == 0 and elseLabel == 0 and forStart == 0:
                    done  = 1
                else:
                    continue

            ## DO WHILE ##
            if line == 'BRANCH LABEL_DO_WHILE':
                whileStart += 1
                if appendVal:
                    appendVal.append('LOOP_DO')
                else:
                    appendVal=['LOOP_DO']
                continue
                # appendVal.append('LOOP')
            elif line == 'BRANCH LABEL_DO_WHILE_END':
                appendVal.append('END_LOOP_DO')
                doWhileEnd = 1
                whileStart -= 1
                if ifLabel == 0 and whileStart == 0 and elseLabel == 0 and forStart == 0:
                    done  = 1
                # else:
                continue

            ## FOR LOOP ##
            if line == 'BRANCH LABEL_FOR':
                forStart += 1
                if appendVal:
                    appendVal.append('LOOP_FOR')
                else:
                    appendVal=['LOOP_FOR']
                continue
            elif line == 'BRANCH LABEL_FOR_END':
                appendVal.append('END_LOOP_FOR')
                forStart -= 1
                if ifLabel == 0 and whileStart == 0 and elseLabel == 0 and forStart == 0:
                    done  = 1
                else:
                    continue

            if ifLabel >= 1 or elseLabel >= 1 or printSet == 1 or whileStart >= 1 or forStart >= 1:
                appendVal.append(line)
            elif done != 1:
                if line == ';':
                    done = 1
                else:
                    if appendVal:
                        appendVal.append(line)
                    else:
                        appendVal = [line]
            elif doWhileEnd == 1:
                doWhileEnd = 0
                if appendVal:
                    appendVal.append(line)
                else:
                    appendVal = [line]

            if done == 1:
                if len(appendVal) == 0:
                    done = 0
                    continue
                print "Val: ", appendVal
                if appendVal[0] in ['if', 'LOOP', 'LOOP_DO', 'LOOP_FOR', 'END_LOOP_DO']:
                    list = []
                    for key in appendVal:
                        if key != ';':
                            list.append(key)
                        else:
                            # print "List ", list
                            if 'print' in list:
                                list.append(';')
                            self.Dict[i] = list
                            list = []
                            i += 1
                    ## For End LOOP Tags ##
                    if len(list) > 0:
                        self.Dict[i] = list
                        list = []
                        i += 1

                else:
                    self.Dict[i] = appendVal
                    i += 1
                appendVal = []
                done = 0
                # flag = 0
        self.lineno = len(self.Dict)
        # for keys in  self.Dict.keys():
        #     print self.Dict[keys]

    # Actual Analysis for each line #
    def graphGen(self):
        '''
        for key in self.Dict.keys():
            list = self.Dict[key]
            length = len(list)
            if length > 1 and list[1] == '=':
                self.Def.append(self.Dict[key][0])
                for i in range(length-1):
                    val = list[i+1]
                    if (val != 'input' and \
                        not re.search('^[0-9]+$', val) and \
                        val not in [')', '(', ';', '='] and \
                        val not in self.umath and \
                        val not in self.symbols):
                        if 'UNARY' in val or 'BINARY' in val:
                            continue
                        else:
                            if i+2 < length-1 and list[i+2] == '=':
                                self.Def.append(val)
                            else:
                                self.Use.append(val)
            elif length > 0 and self.Dict[key][0] == 'print':
                ## Update use variable ##
                for val in list[1:]:
                    if (not re.search('^[0-9]+$', val) and \
                        val not in [')', '(', ';', '='] and \
                        val not in self.umath and \
                        val not in self.symbols):
                        if 'UNARY' in val or 'BINARY' in val:
                           continue
                        else:
                            self.Use.append(val)
            else:
                ## Handling If and While ##
                # length = len(list)
                if length > 1:
                    # print list
                    for val in list[1:]:
                        if (not re.search('^[0-9]+$', val) and \
                            val not in [')', '(', ';', '='] and \
                            val not in self.umath and \
                            val not in self.symbols):
                            if 'UNARY' in val or 'BINARY' in val:
                                continue
                            else:
                                self.Use.append(val)

            # At each line we computed the Use, Defined lists.
            ## Removing 'Memory' entries from Def and Use ##
            if 'memory' in self.Def:
                self.Def.remove('memory')
            if 'memory' in self.Use:
                self.Use.remove('memory')

            self.variables = self.variables.union(sets.Set(self.Def))
            self.variables = self.variables.union(sets.Set(self.Use))
            # print self.variables, "      Variables"
            self.defDict[key] = self.Def
            self.useDict[key] = self.Use
            self.Def = []
            self.Use = []

        '''
        lno = 0
        for line in self.stmt:
            # print line
            if 'variable_' in line:
                # print line
                list = re.split(' ', line)
                if 'variable_' in list[1]:
                    # print lno, list[1]
                    end = list[1].index(',')
                    var = list[1][9:end]
                    self.variables = self.variables.union(sets.Set([var]))
                    if list[0] == 'ori':
                        self.defDict[lno] = [var]
                        self.useDict[lno] = []
                    elif list[0] == 'sw':
                        ## memory = variable ##
                        # print list
                        self.useDict[lno] = [var]
                        self.defDict[lno] = []
                    elif list[0] == 'lw':
                        ## variable = memory ##
                        # print list
                        self.defDict[lno] = [var]
                        self.useDict[lno] = []
                elif 'variable_' in list[2]:
                    # print lno, list[2]
                    end = list[2].index(',')
                    var = list[2][9:end]
                    self.variables = self.variables.union(sets.Set([var]))
                    if list[0] == 'ori':
                        self.useDict[lno] = [var]
                        self.defDict[lno] = []
            else:
                self.defDict[lno] = []
                self.useDict[lno] = []
            lno += 1
        self.lineno = lno
        # print self.variables

        # print self.useDict
        # for i in range(lno):
        #     if self.defDict[i+1]:
        #         print "Definitions: ", self.defDict[i+1]
        #     if self.useDict[i+1]:
        #         print "Use: ", self.useDict[i+1]
        # sys.exit(-1)
        # Computing In and Out at each Line #
        # in(s) = use(s) U (out(s) - def(s))
        # out(s) = U of all successors of in(s)
        ## For Loops and Control Structures ##
        while True:
            tempInDict = copy.deepcopy(self.inDict)
            # self.lineno = len(self.inDict)
            for i in range(self.lineno):
                self.Def = self.defDict[self.lineno - i - 1]
                self.Use = self.useDict[self.lineno - i - 1]
                # if self.inDict and self.inDict[i]:
                #     self.inSet = self.inDict[self.lineno - i - 1]
                #     self.outSet = self.outDict[self.lineno - i - 1]
                # else:
                self.inSet = sets.Set([])
                self.outSet = sets.Set([])

                if i != 0:
                    x = self.lineno - i
                    self.outSet = self.inDict[x]

                self.inSet = sets.Set(self.Use).union(self.outSet.difference(sets.Set(self.Def)))
                self.outDict[self.lineno - i - 1] = self.outSet
                self.inDict[self.lineno - i - 1] = self.inSet
            if tempInDict == self.inDict:
                break

        # for i in range(self.lineno):
        #     print " In: ", self.inDict[i], " Use : ", self.useDict[i], " Def: ", self.defDict[i]
        # print "In Dict: ", self.inDict
        # print "Out Dict: ", self.outDict
        # print variables

        ## Checking for static semantics ##
        # print self.inS

        ## Generating Interference Graph ##
        for i in self.variables:
            unionSet = sets.Set([])
            tempSets = [x for x in self.inDict.values() if i in x]
            for x in tempSets:
                unionSet = unionSet.union(x)
            self.graph[i] = unionSet.difference([i])

    ## Register allocation ##
    def removeEdgesIncidentFromDict(self,element):
        for i in self.graph[element]:
            adj = self.graph[i]
            adj.remove(element)
        self.graph.pop(element)

    def allocateRegisters(self, g, element, k):
        reg = copy.deepcopy(self.registers[:k])
        for adj in g[element]:
            if adj in self.allocReg.keys() and self.allocReg[adj] in reg:
                reg.remove(self.allocReg[adj])
        if len(reg) != 0:
            self.allocReg[element] = reg[0]
        else:
            self.spill = element
            print "Cannot allocate registers for the element: %s" %(element)

    def getMaxEdgesNode(self, g):
        max = 0
        node = ''
        for x in g.keys():
            length = len(g[x])
            if max <= length:
                node = x
                max = length
        return node

    ## Deprecated ##
    def reconstructGraph(self, element):
        list1 = ['memory', '=', element+'1',';']
        list2 = [element+'2','=','memory',';']
        idx1 = self.stmt.index(element,0)
        self.stmt[idx1] = element+'1'
        idx2 = self.stmt.index(';',idx1+1)
        temp = []
        temp = self.stmt[:idx2+1] + list1 + self.stmt[idx2+1:]
        self.stmt = copy.deepcopy(temp)
        idx1 = self.stmt.index(element,idx2+1+len(list1))
        while self.stmt[idx1] != ';':
            # Do nothing
            idx1 -= 1
        temp = self.stmt[:idx1+1] + list2 + self.stmt[idx1+1:]
        self.stmt = copy.deepcopy(temp)
        length = len(self.stmt)
        idx1 += len(list2)
        while idx1 < length:
            if element in self.stmt:
                idx1 = self.stmt.index(element, idx1)
                self.stmt[idx1] = element+'2'
            else:
                break

    def max(self, i, j):
        if i > j:
            return i
        else:
            return j

    def getAssignmentList(self, element, n):
        return ['memory', '=', element,';']

    def getElementFromMemoryList(self, element, n):
        return [element,'=','memory',';']

    def checkForUnaryElement(self, stmt, prevIdx, element):
        ret = -1
        str = 'UNARY '
        for i in self.unaryOps:
            if str+i+element in stmt[prevIdx:]:
                minIdx = stmt.index(str+i+element, prevIdx)
                if ret == -1:
                    ret = minIdx
                else:
                    ret = min(ret, minIdx)
                # break
        return ret

    def reconstructGraph2(self, element):
        '''
        count = 1
        length = len(self.stmt)
        list1 = ['memory', '=', element,';']
        list2 = [element,'=','memory',';']
        prevIdx = 0
        while prevIdx < length:
            ## Finding the element being defined ##
            idx1 = 0
            uidx = self.checkForUnaryElement(self.stmt, prevIdx, element)

            if element not in self.stmt[prevIdx:] and uidx < 0:
                break
            idx1 = self.stmt.index(element,prevIdx)
            if uidx > 0 and idx1 > uidx:
                idx1 = uidx
            # if not idx1:
            #     break
            idx2 = self.stmt.index(';',idx1+1)
            if not idx2:
                break
            temp = []
            llen = len(list1)
            if self.stmt[idx1+1] == '=':
                temp = self.stmt[:idx2+1] + list1 + self.stmt[idx2+1:]
                self.stmt = copy.deepcopy(temp)
                prevIdx = self.stmt.index(';',idx2 + llen - 1)
                length += 4
            else:
                prevIdx = idx2 + llen + 1
                while self.stmt[idx1] != ';':
                    # Do nothing
                    idx1 -= 1
                llen = len(list2)
                temp = self.stmt[:idx1+1] + list2 + self.stmt[idx1+1:]
                self.stmt = copy.deepcopy(temp)
                length += 4
            count += 1
            '''
        # print self.stmt
        # print
        self.memory[element] = self.memcount
        self.memcount += 4
        list = ['la $t8, memory']
        val1 = ['sw variable_%s, %d($t8)' %(element, self.memory[element])]
        val2 = ['lw variable_%s, %d($t8)' %(element, self.memory[element])]
        # list.append(val)
        index = 0
        tempList = []
        length = len(self.stmt)
        for lno in range(length):
            line = self.stmt[index]
            if 'variable_'+element+',' in line:
                # print "Start at lno: ", lno
                linelist = re.split(' ', line)
                if linelist[1] == 'variable_'+element+',':
                    ## memory = variable ##
                    # list.append(val1)
                    # print self.stmt[:index+1]
                    # print
                    # print
                    # print self.stmt[index+1:]
                    tempList = self.stmt[:index+1] + list + val1 + self.stmt[index+1:]
                    index += 2
                    # lno += 3
                else:
                    ## variable = memory ##
                    # list.append(val2)
                    tempList = self.stmt[:index] + list + val2 + self.stmt[index:]
                    index += 2
                    # lno += 3
                if tempList:
                    self.stmt = tempList
                    # print "Updated line at lno: ", lno
            index += 1
        # print self.stmt
        # sys.exit(-1)

    def graphColoring(self, k):
        g = self.graph
        stack = []
        tempGraph = copy.deepcopy(g)
        while len(g) != 0:
            for v in g.keys():
                if len(g[v]) >= k:
                    continue
                self.removeEdgesIncidentFromDict(v)
                stack.append(v)
            # Spilling #
            if len(g) != 0:
                v = self.getMaxEdgesNode(g)
                self.removeEdgesIncidentFromDict(v)
                stack.append(v)
        while len(stack) != 0:
            element = stack.pop(-1)
            self.allocateRegisters(tempGraph, element, k)
            if element not in self.allocReg.keys():
                return -1
        return 0

    ## Deprecated, this is handled in Parser ##
    def replaceBoolValues(self):
        if 'true' in self.stmt or 'false' in self.stmt:
            self.stmt = ['1' if x == 'true' else x  for x in self.stmt]
            self.stmt = ['0' if x == 'false' else x  for x in self.stmt]
        # print self.stmt
        # sys.exit(0)

    ## For Homework-05 ##
    def removeTypes(self, list):
        # tempList = copy.deepcopy(list)
        # print list
        # print
        # print
        array = 0
        tempList = []
        typeStart = 0
        for i in list:
            if 'TYPE' in i:
                typeStart = 1
                if '[]' in i:
                    array = 1
                else:
                    array = 0
                # tempList.remove(i)
                continue
            if typeStart == 1 and i != ';':
                if array != 1 and i != ',':
                    self.nonArrayVar.add(i)
                # tempList.remove(i)
                continue
            else:
                # if typeStart == 1 and i == ';':
                #     continue
                tempList.append(i)
                typeStart = 0
        while ';' in tempList:
            tempList.remove(';')
        # print self.nonArrayVar
        return tempList

    def updateDict(self, dict, key, val):
        if key in dict.keys():
            dict[key].append(val)
        else:
            dict[key] = [val]
        return dict

    def updateVarBasedOnBlock(self, i, updt, blockno, varDict):
        # i - string
        # updt - list of variables to be updated
        # blockno - variable should be appended with var_blockno
        if len(updt) == 0:
            return i
        else:
            for var in updt:
                if 'variable_'+var+',' in i:
                    ## Replace variable_$var with variable_$var_blockno ##
                    # i = re.sub('variable_'+var,'variable_'+var+'_'+str(blockno), i)
                    i = re.sub('variable_'+var+',','variable_'+var+'_'+str(varDict[var])+',', i)
                    # print
                    # print "Updated to - ", i
                elif i == var:
                    ## For Type - Declarations ##
                    ## Later stages, variables are enumerated for further analysis ##
                    # i = re.sub(var,var+'_'+str(blockno), i)
                    i = re.sub(var,var+'_'+str(varDict[var]), i)
                    # print
                    # print "Updated to - ", i
        return i

    def checkIfVarIsAlreadyPresent(self, varDict, blockno, i):
        # i - Line to be validated for the variables
        for block in range(blockno):
            if block in varDict.keys():
                if i in varDict[block]:
                    return True
        return False

    def blockVariableUpdates(self, stmt):
        blockno = 0
        typeStart = 0
        varDict = {}
        updt = []
        tempList = []
        variables = {}
        for i in stmt:
            if i == 'BLOCK_START':
                blockno +=1
                if blockno in varDict.keys():
                    varDict.pop(blockno)
                # continue
            elif i == 'BLOCK_END':
                blockno -= 1
                updt = []
                # continue
            elif 'TYPE' in i:
                typeStart = 1
                # continue
            elif typeStart == 1 and i != ';':
                if i != ',':
                    # Have to update the updt list based on redundancy #
                    if self.checkIfVarIsAlreadyPresent(varDict, blockno, i):
                        ## Already Present ##
                        ## Update updt list accordingly ##
                        ## As `i' is a variable so no need to do extra parsing ##
                        # print "Working on variable: ", i
                        updt.append(i)
                    varDict = self.updateDict(varDict, blockno, i)
                    if i in variables.keys():
                        variables[i] += 1
                    else:
                        variables[i] = 1
                # continue
            else:
                typeStart = 0
            ## Generic updates on `i' based on the block ##
            i = self.updateVarBasedOnBlock(i, updt, blockno, variables)
            tempList.append(i)
        print varDict
        # print
        # print tempList
        return tempList


    # Starts the register allocation algorithm based on the number of registers #
    def run(self):
        ret = -1
        count = 0
        ## Bool values are already replaced as 0 and 1 in parser ##
        # self.replaceBoolValues()
        # self.staticSemanticCheck()
        # self.buildDictionary()

        newstmt = copy.deepcopy(self.stmt)
        ## Renames the variables if the current block  ##
        ## has a variable which is defined in previous ##
        ## blocks. This avoids confusion in liveness   ##
        newstmt = self.blockVariableUpdates(newstmt)
        newstmt = self.removeTypes(newstmt)
        # print newstmt
        newstmt = self.removeUnusedAssignments2(newstmt)

        ## Define Before Use check ##
        ## Will do once the liveness is completed ##
        # self.semanticsAssignmentCheck()

        # self.stmt = self.removeUnusedAssignments(newstmt)
        self.stmt = newstmt

        while ret != 0:
            self.graphGen()
            count += 1
            ret = self.graphColoring(3)
            if ret != 0:
                print "Retrying..!"
                # sys.exit(-1)
                self.reconstructGraph2(self.spill)
                self.reset()
            else:
                break
            if count == 10:
                print "\nRegister Allocation Failed due to unavailability of required number of registers.!"
                sys.exit(-1)
        print "Liveness analysis completed successfully.!"