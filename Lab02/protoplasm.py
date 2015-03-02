##########################################################################################################
## protoplasm - A simple compiler to compile a simple calculator program (XXX.proto)			##
##													##
## Usage:												##
##	python[.exe] protoplasm.py <proto source filename>						##
##													##
## Name: 	Rajendra Kumar Raghupatruni		    						##
## SBU Net ID: 	rraghuaptrun				    						##
## SBU ID: 	109785402				    						##
##########################################################################################################

import sys, SyntaxSemanticAnalysis

def usage():
    print "\nUsage:"
    print "python[.exe] protoplasm.py <proto source file name>"

def commandlineCheck():
    if len(sys.argv) != 2:
        print "Error in number of arguments."
        usage()
        sys.exit(0)

if __name__ == '__main__':
    commandlineCheck()
    extremeOpt = 1
    syntaxCheck = SyntaxSemanticAnalysis.SyntaxSemanticAnalysis(sys.argv[1], extremeOpt)
    syntaxCheck.run()
