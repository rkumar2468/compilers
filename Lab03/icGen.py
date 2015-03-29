import re

class AST:
    def __init__(self, data):
        self.data = data
        self.ic = ''

    def removeComments(self):
        if self.data:
            temp = re.sub(r'\/\/.*','',self.data)
            self.data = temp

    def generateICode(self):
        if self.data:
            self.removeComments()
            code = re.split('\n',self.data)
            # print code
            for line in code:
                # if line == '\t' or line == ' ' or line == '\n':
                #     continue
                # print line
                if re.match('if', line):
                    print "testing"
                else:
                    self.ic += line
        else:
            return