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
##	python[.exe] protoplasm5.py <proto source filename>						                            ##
##													                                                    ##
## Name: 	    Rajendra Kumar Raghupatruni		    						                            ##
## SBU Net ID: 	rraghuaptrun				    						                                ##
## SBU ID: 	    109785402				    						                                    ##
##########################################################################################################

import sys, Parser_05

copypropagation = 0
constpropagation = 0
loopinvariant = 0
commonsubexpelim = 0

def usage():
    print "\nUsage:"
    print "python[.exe] protoplasm5.py <proto source file name> [--opt=<on/off>]"
    print "opt: constantpropagation copypropagation cselimination loopmotion inductionvariables"
    print "Note: Induction Variables - not implemented"

def commandlineCheck():
    if len(sys.argv) < 2:
        print "Error in number of arguments. ", len(sys.argv)
        usage()
        sys.exit(0)
    else:
        global copypropogation, copypropagation, loopinvariant, commonsubexpelim
        if "--constantpropagation=on" in sys.argv:
            constpropagation = 1
        if "--copypropagation=on" in sys.argv:
            copypropagation = 1
        if "--cselimination=on" in sys.argv:
            commonsubexpelim = 1
        if "--loopmotion=on" in sys.argv:
            loopinvariant = 1

def readInput(fid):
    inp = ''
    for line in fid:
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
        Parser_05.run(data, copypropagation, constpropagation, loopinvariant, commonsubexpelim)
    else :
        print "File: <%s> is empty.!" %(fileName)
        sys.exit(-1)

    ## Static Semantic Analysis ##
    print "Intermediate Code: ", Parser_05.intermediateCode
    print copypropagation
    print

    # '''
    # Live Analysis ##
    import liveanalysis
    live = liveanalysis.LiveAnalysis(Parser_05.intermediateCode, copypropagation, constpropagation, loopinvariant, commonsubexpelim)
    live.run()
    print live.allocReg
    # print live.Dict


    asmfile = fileName.split('.')[0]+'.asm'
    removeVariables = []

    # '''
    ## Final Code Generation ##
    import CGen
    cgen = CGen.CodeGen(asmfile, live.allocReg, live.stmt)
    cgen.generateIntermediateCode()
    cgen.generateASM()
    # '''