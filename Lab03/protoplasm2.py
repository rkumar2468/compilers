##########################################################################################################
## protoplasm2 - A simple compiler to compile a program (XXX.proto) with the below features			    ##
##													                                                    ##
## 1. Operators: +, -, *, /, %, &&, ||, !, Unary -,                                                     ##
##													                                                    ##
## 2. Supports Single Line comments like Java "//"                                                      ##
##													                                                    ##
## 3. Control Structures: IF THEN ELSE, WHILE DO                                                        ##
##													                                                    ##
## 4. STDIN/STDOUT: input/print                                                                         ##
##                                                                                                      ##
## Usage:											                                                	##
##	python[.exe] protoplasm2.py <proto source filename>						                            ##
##													                                                    ##
## Name: 	    Rajendra Kumar Raghupatruni		    						                            ##
## SBU Net ID: 	rraghuaptrun				    						                                ##
## SBU ID: 	    109785402				    						                                    ##
##########################################################################################################

import sys, icGen, Parser

def usage():
    print "\nUsage:"
    print "python[.exe] protoplasm2.py <proto source file name>"

def commandlineCheck():
    if len(sys.argv) != 2:
        print "Error in number of arguments."
        usage()
        sys.exit(0)

def readInput(fid):
    inp = ''
    for line in fid:
        # print line
        inp += line
    return inp

if __name__ == '__main__':

    ## Command Line Arguments Check ##
    commandlineCheck()

    ## Lexing and Parsing - With Static Semantic Check ##
    fileName = sys.argv[1]

    ## Opening the <XYZ>.proto file in read mode ##
    fid = open(fileName, 'r')
    data = readInput(fid)

    ## Closing the opened file descriptor ##
    fid.close()

    if data:
        Parser.run(data)
    else :
        print "File: <%s> is empty.!" %(fileName)
        sys.exit(-1)
    print "Intermediate Code: ", Parser.intermediateCode

    import liveanalysis
    live = liveanalysis.LiveAnalysis(Parser.intermediateCode)
    live.run()
    print live.allocReg

    asmfile = fileName.split('.')[0]+'.asm'

    cgen = CGen.CodeGen(self.asmfile, live.allocReg, self.Dict, self.removeVariables)
    cgen.generateIntermediateCode()
    cgen.generateASM()