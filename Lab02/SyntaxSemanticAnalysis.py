##########################################################################################################
## Class: SyntaxSemanticAnalysis									##
## This class is responsible to perform syntax analysis and semantic analysis				##
## run () is a wrapper which checks for the syntax and semantic errors					##
##													##
## Name: 	Rajendra Kumar Raghupatruni		    						##
## SBU Net ID: 	rraghuaptrun				    						##
## SBU ID: 	109785402				    						##
##########################################################################################################

import sys, tokenize, copy, liveanalysis, re, CGen


class SyntaxSemanticAnalysis:
    def __init__(self, file, optimization):
        """List of keywords supported in this compiler."""
        self.keywords = ['print','input']
        self.math = ['+','-','*','/','%']
        self.lhs =[]
        self.rhs = []
        self.source = []
        self.braceOpen = 0
        self.braceClose = 0
        self.assigned = []
        self.ic = []
        self.Dict = {}
        self.fid = open(file, 'r')
        self.asmfile = file.split('.')[0]+'.asm'
        self.tokens = ''
        self.eq = 0
        self.start = 1
        self.var = 0
        self.prn = 0
        self.inp = 0
        self.variable = 0
        self.sym = 0
        self.printExp = 0
        self.assignment = ''
        self.printval = ''
        self.assignedval = ''
        self.optLevel = optimization
        self.removeVariables = []

    def cleanLists(self):
        self.lhs =[]
        self.rhs = []
        self.source = []
        self.assigned = []
        self.ic = []
        self.removeVariables = []

    def buildDict(self, stmt):
        i = 0
        self.Dict = {}
        lineno = 0
        length = len(stmt)
        while i < length:
            idx = stmt.index(';',i)
            [line, something] = [stmt[i:idx], stmt[idx+2:]]
            self.Dict[lineno]= line
            lineno += 1
            i = idx + 1
            # print line

    def reset(self):
        self.braceClose = 0
        self.braceOpen = 0
        self.eq = 0
        self.start = 1
        self.var = 0
        self.prn = 0
        self.inp = 0
        self.variable = 0
        self.sym = 0
        self.numb = 0
        self.printExp = 0
        self.assignment = ''
        self.printval = ''
        self.assignedval = ''

    def SyntaxCheck(self):
        # Syntax Checking #
        count = 0
        self.tokens = tokenize.generate_tokens(self.fid.readline)
        """ Token numbers: 51 - symbol, 0 - EOF, 4 - CR """
        for tnum, token,val1,val2,val3 in self.tokens:
            # New Line and EOF checking.
            if tnum == 4 or tnum == 0 or tnum == 54:
                continue
            self.source.append(token)
            if self.start == 1:
                self.start = 0
                count = 0
                if tnum != 1:
                    """ First token should either be a variable or print """
                    print "Syntax Error: Invalid token \'%s\'" %(token)
                    self.fid.close()
                    # self.asmfid.close()
                    sys.exit(-1)
                elif token == 'input':
                    print "Syntax Error: Invalid use of token \'%s\'" %(token)
                    sys.exit(-1)
                if token != 'print':
                    self.lhs.append(token)
                    self.var = 1
                    self.assignment = token
                else:
                    self.prn = 1
                    self.printExp = 1
                    count = 0
            else:
                # count += 1
                if self.var == 1:
                    if token == '=':
                        self.eq = 1
                        self.var = 0
                        count = 0
                        # self.assigned.append(self.source[-2])
                    else:
                        print "Syntax Error: Invalid token %s"
                        self.reset()
                        self.cleanLists()
                        self.fid.close()
                        # self.asmfid.close()
                        sys.exit(-1)

                elif token == 'print':
                    if self.source[-2] in self.math or self.eq == 1:
                        print "Syntax Error: Invalid use of the keyword \'print\'"
                    else:
                        print "Syntax Error: Semicolon missing"
                    self.fid.close()
                    # self.asmfid.close()
                    sys.exit(-1)

                elif self.prn == 1:
                    self.prn = 0
                    if token != '(':
                        print "Syntax Error: No braces found for print statement"
                        self.fid.close()
                        # self.asmfid.close()
                        sys.exit(-1)
                    self.braceOpen = 1

                elif self.eq == 1:
                    if token != 'input' and tnum != 1 and tnum != 2:
                        print "Syntax Error: Invalid use of \'%s\'" %(token)
                        self.fid.close()
                        # self.asmfid.close()
                        sys.exit(-1)
                    elif token == "input":
                        self.inp = 1
                    elif tnum == 1:
                        self.variable = 1
                        count += 1
                        if token not in self.assigned:
                            print "Semantic Error: Used undefined variable \'%s\'" %(token)
                            self.reset()
                            self.cleanLists()
                            self.fid.close()
                            # self.asmfid.close()
                            sys.exit(-1)
                    elif tnum == 2:
                        self.numb = 1
                        count += 1
                    self.eq = 0

                elif self.braceClose and token != ';':
                    print "Syntax Error: Semicolon missing after \')\'"
                    self.fid.close()
                    # self.asmfid.close()
                    sys.exit(-1)

                elif token == ';':
                    if self.braceOpen != self.braceClose:
                        print "Syntax Error: Invalid use of braces"
                        self.fid.close()
                        # self.asmfid.close()
                        sys.exit(-1)
                    # variable or number or close brace #
                    elif self.inp == 1 and (self.braceOpen != 1 or self.braceClose != 1):
                        print "Syntax Error: Invalid use of braces"
                        sys.exit(-1)
                    elif self.sym == 1 and count < 2:
                        print "Syntax Error: Invalid use of symbol \'%s\'" %(self.source[-2])
                        self.fid.close()
                        # self.asmfid.close()
                        sys.exit(-1)
                    # print len(self.assignment), self.assignment
                    if len(self.assignment) != 0:
                        self.assigned.append(self.assignment)
                    self.reset()

                elif token == '(':
                    # Only print and input can have braces. #
                    if self.source[-2] not in self.keywords:
                        print "Syntax Error: Invalid use of braces"
                        self.fid.close()
                        # self.asmfid.close()
                        sys.exit(-1)
                    self.braceOpen = 1

                elif token == ')':
                    # If there is already a braceClose seen or there is no braceOpen within the same line.
                    if self.braceClose == 1 or self.braceOpen == 0 or (self.inp == 1 and self.source[-2] != '('):
                        print "Syntax Error: Invalid use of braces"
                        self.fid.close()
                        # self.asmfid.close()
                        sys.exit(-1)
                    self.braceClose = 1

                elif tnum == 1:
                    count += 1
                    if (self.variable == 1 or self.numb == 1) and count > 2:
                        print "Syntax Error: Semicolon missing"
                        self.fid.close()
                        # self.asmfid.close()
                        sys.exit(-1)
                    elif self.source[-2] not in ['=', '('] and self.source[-2] not in self.math:
                        print "Syntax Error: Improper use of \'%s\'" %(token)
                        self.fid.close()
                        # self.asmfid.close()
                        sys.exit(-1)
                    if token not in self.assigned:
                        print "Semantic Error: Used undefined variable \'%s\'" %(token)
                        self.reset()
                        self.cleanLists()
                        self.fid.close()
                        # self.asmfid.close()
                        sys.exit(-1)
                    self.variable = 1

                elif token in self.math:
                    if self.sym == 1 or (self.variable != 1 and self.numb != 1):
                        print "Syntax Error: Invalid use of token \'%s\'" %(token)
                        self.fid.close()
                        # self.asmfid.close()
                        sys.exit(-1)
                    self.sym = 1

                elif tnum == 2:
                    # Number check
                    count += 1 
		    self.numb = 1
                    if self.source[-2] not in self.math and self.eq != 1 and self.braceOpen != 1 or self.braceClose == 1:
                        print "Syntax Error: Invalid use of token \'%s\'" %(token)
                        self.fid.close()
                        # self.asmfid.close()
                        sys.exit(-1)
        # print self.source
        self.fid.close()
        print "Syntax and Semantic Analysis - Success.!"

    def deleteFromPos(self, stmt,i):
        if ';' in stmt[i:]:
            idx = stmt.index(';',i)
            while stmt[idx-1] != ';':
                stmt.pop(idx)
                idx -=  1
                if len(stmt) == 0:
                    break
            if len(stmt) != 0:
                stmt.pop(idx)
        return stmt

    def removeUnusedVariables(self, stmt):
        length = len(stmt)
        lastkey = self.Dict.keys()[-1]
        prevIndex = 0
        for key in self.Dict.keys():
            val = self.Dict[key]
            if 'print' not in val and key < lastkey:
                index = stmt.index(val[0], prevIndex)
		tempidx = stmt.index(';', index)
                if val[0] in stmt[tempidx+1:]:
                    index2 = stmt.index(val[0],index+1)
                    if stmt[index2-1] == ';' or stmt[index2+1] == '=':
                        if 'input' not in val:
                            stmt = self.deleteFromPos(stmt,index)
                            prevIndex = prevIndex - len(val) - 1
                else:
                    if 'input' not in val:
                        stmt = self.deleteFromPos(stmt,index)
                        prevIndex = prevIndex - len(val) - 1
                    else:
                        self.removeVariables.append(val[0])
                    break
            prevIndex += len(val) + 1
        return stmt

    def listscheck(self, list1, list2):
        if len(list1) != len(list2):
            return False
        i = 0
        for i in range(len(list1)):
            if list1[i] == list2[i]:
                continue
            else:
                return False
        return True

    def run(self):
        self.SyntaxCheck()
        stmt = copy.deepcopy(self.source)
        self.buildDict(stmt)
        count = 0
        if self.optLevel == 0:
            newstmt = []
            newstmt = self.removeUnusedVariables(stmt)
            self.buildDict(newstmt)
        else:
            newstmt = []
            cmpstmt = copy.deepcopy(stmt)
            while True:
                # print cmpstmt
                count += 1
                newstmt = self.removeUnusedVariables(stmt)
                boolval = self.listscheck(newstmt, cmpstmt)
                # print boolval
                if boolval == False and len(newstmt) != 0:
                    self.buildDict(newstmt)
                    cmpstmt = copy.deepcopy(newstmt)
                    self.removeVariables = []
                else:
                    # print newstmt
                    break
        if len(newstmt) > 0:
            live = liveanalysis.LiveAnalysis(newstmt)
            live.run()
            if self.listscheck(newstmt, live.getLAStmt()) == False:
                newstmt = live.getLAStmt()
                self.buildDict(newstmt)
            # print newstmt
            # print "\nIntermediate Code:"
            print live.allocReg

            cgen = CGen.CodeGen(self.asmfile, live.allocReg, self.Dict, self.removeVariables)
            cgen.generateIntermediateCode()
            cgen.generateASM()
        else:
            print "\nNo code generation required.!\n"
