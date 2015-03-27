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
        flag = 0
        for line in self.stmt:
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
                if ifLabel == 0 and whileStart == 0 and elseLabel == 0:
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
                if ifLabel == 0 and whileStart == 0 and elseLabel == 0:
                    done  = 1
                else:
                    continue
            elif line == 'BRANCH LABEL_IF_END':
                appendVal.append('if_end')
                appendVal.append(';')
                ifLabel -= 1
                if ifLabel == 0 and whileStart == 0 and elseLabel == 0:
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
                if ifLabel == 0 and whileStart == 0 and elseLabel == 0:
                    done  = 1
                else:
                    continue

            if ifLabel >= 1 or elseLabel >= 1 or printSet == 1 or whileStart >= 1:
                appendVal.append(line)
            elif done != 1:
                if line == ';':
                    done = 1
                else:
                    if appendVal:
                        appendVal.append(line)
                    else:
                        appendVal = [line]

            if done == 1:
                if len(appendVal) == 0:
                    done = 0
                    continue
                # print "Val: ", appendVal
                if appendVal[0] in ['if', 'LOOP']:
                    list = []
                    for key in appendVal:
                        if key != ';':
                            list.append(key)
                        else:
                            # print "List ", list
                            self.Dict[i] = list
                            list = []
                            i += 1
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
        # print self.Dict
        # return
        for key in self.Dict.keys():
            list = self.Dict[key]
            if len(list) > 1 and list[1] == '=':
                self.Def.append(self.Dict[key][0])
                for val in list[2:]:
                    if (val != 'input' and not re.search('^[0-9]+$', val) and val not in [')', '(', ';']):
                        if 'UNARY' in val:
                            variable = val[7:]
                            if (not re.search('^[0-9]+$', variable)):
                                self.Use.append(variable)
                        elif 'BINARY' in val:
                            continue
                        else:
                            self.Use.append(val)

            elif self.Dict[key][0] == 'print':
                ## Update use variable ##
                for val in list[1:]:
                    if (not re.search('^[0-9]+$', val) and val not in [')', '(', ';']):
                        if 'UNARY' in val:
                            variable = val[7:]
                            if (not re.search('^[0-9]+$', variable)):
                                self.Use.append(variable)
                        elif 'BINARY' in val:
                            continue
                        else:
                            self.Use.append(val)
            else:
                ## Handling If and While ##
                length = len(list)
                if length > 1:
                    # print list
                    for val in list[1:]:
                        if (not re.search('^[0-9]+$', val) and val not in [')', '(', ';']):
                            if 'UNARY' in val:
                                # if self.Use:
                                variable = val[7:]
                                if (not re.search('^[0-9]+$', variable)):
                                    self.Use.append(variable)
                            elif 'BINARY' in val:
                                continue
                            else:
                                self.Use.append(val)

            # print "Data :", list, self.Def, self.Use
            # At each line we computed the Use, Defined lists.
            self.variables = self.variables.union(sets.Set(self.Def))
            self.variables = self.variables.union(sets.Set(self.Use))
            self.defDict[key] = self.Def
            self.useDict[key] = self.Use
            self.Def = []
            self.Use = []


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

        print self.inDict, self.outDict
        # print variables
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

    # Starts the register allocation algorithm based on the number of registers #
    def run(self):
        ret = -1
        count = 0
        while ret != 0:
            self.buildDictionary()
            self.graphGen()
            count += 1
            ret = self.graphColoring(7)
            if ret != 0:
                self.reconstructGraph(self.spill)
                self.reset()
            else:
                break
            if count == 10:
                print "\nRegister Allocation Failed due to unavailability of required registers.!"
                sys.exit(-1)