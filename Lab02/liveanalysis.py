##########################################################################################################
## Class: LiveAnalysis											##
## This class is responsible to allocate registers to the variables of the proto file			##
## run () is a wrapper which checks for the register allocation 					##
##													##
## Name: 	Rajendra Kumar Raghupatruni		    						##
## SBU Net ID: 	rraghuaptrun				    						##
## SBU ID: 	109785402				    						##
##########################################################################################################

import re, sets, copy, sys

# Live analysis #
class LiveAnalysis:
    def __init__(self, stmt):
        self.stmt = stmt
        self.math = ['+','-','*','/','%']
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
        length = len(self.stmt)
        while i < length:
            idx = self.stmt.index(';',i)
            [line, something] = [self.stmt[i:idx], self.stmt[idx+2:]]
            self.Dict[self.lineno]= line
            self.lineno += 1
            i = idx + 1

    # Actual Analysis for each line #
    def graphGen(self):
        for key in self.Dict.keys():
            if self.Eq in self.Dict[key]:
                if self.Dict[key][0] != 'memory':
                    self.Def = [self.Dict[key][0]]
                if self.inp not in self.Dict[key]:
                   for val in self.Dict[key][2:]:
                       if (not re.search('^[0-9]+$', val)) and (val not in self.math) and (val != 'memory'):
                           self.Use.append(val)
            elif 'print' in self.Dict[key]:
                for val in self.Dict[key][2:]:
                   if (not re.search('^[0-9]+$', val)) and (val not in self.math) and (val != ')') and (val != 'memory'):
                       self.Use.append(val)

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
        for i in range(self.lineno):
            self.Def = self.defDict[self.lineno - i - 1]
            self.Use = self.useDict[self.lineno - i - 1]
            self.inSet = sets.Set([])
            self.outSet = sets.Set([])
            
            if i != 0:
                x = self.lineno - i
                self.outSet = self.inDict[x]

            self.inSet = sets.Set(self.Use).union(self.outSet.difference(sets.Set(self.Def)))
            self.outDict[self.lineno - i - 1] = self.outSet
            self.inDict[self.lineno - i - 1] = self.inSet
            
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

