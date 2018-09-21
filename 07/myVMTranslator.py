import sys
from os import listdir
from os.path import isfile, join

# Gets the dir path from command line and name of all files with the .vm extenstion
# The new .asm file will be in the same dir with the dir name
dir_path = sys.argv[1]
file_list = []
for file in listdir(dir_path):
    if file[-3:] == '.vm':
        file_list.append(file)
dir_path = dir_path[::-1]
dir_index = dir_path.index('\\')
dir_name = dir_path[:dir_index]
dir_name = dir_name[::-1]
dir_path = dir_path[::-1]


class Translator():
    def __init__(self):
        self.count = 0
        self.funcName = ''
        self.currfilename = ''
        self.ADD = ['//add', '@SP', 'AM=M-1', 'D=M', 'A=A-1', 'M=M+D']
        self.SUB = ['//sub', '@SP', 'AM=M-1', 'D=M', 'A=A-1', 'M=M-D']
        self.AND = ['//and', '@SP', 'AM=M-1', 'D=M', 'A=A-1', 'M=M&D']
        self.OR = ['//or', '@SP', 'AM=M-1', 'D=M', 'A=A-1', 'M=M|D']
        self.NEG = ['//neg', '@SP', 'A=M-1', 'M=-M']
        self.NOT = ['//not', '@SP', 'A=M-1', 'M=!M']
        self.POP = ['@R13', 'M=D', '@SP', 'AM=M-1', 'D=M', '@R13', 'A=M', 'M=D']
        self.PUSH = ['@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
        self.RETURN = ['//return', '@LCL', 'D=M', '@5', 'A=D-A', 'D=M', '@R13', 'M=D', '@SP', 'A=M-1',
                       'D=M',  '@ARG', 'A=M', 'M=D', 'D=A+1', '@SP', 'M=D', '@LCL', 'AM=M-1',
                       'D=M', '@THAT', 'M=D', '@LCL', 'AM=M-1', 'D=M', '@THIS', 'M=D',
                       '@LCL', 'AM=M-1', 'D=M', '@ARG', 'M=D', '@LCL', 'A=M-1', 'D=M', '@LCL',
                       'M=D', '@R13', 'A=M', '0;JMP']

    def nextCount(self):
        # Used for keeping track of jump conditions
        self.count += 1
        return str(self.count)

    def EQ(self):
        n = self.nextCount()
        s = ['//eq', '@SP', 'AM=M-1', 'D=M', 'A=A-1',
             'D=D-M', '@EQ.true.' + n, 'D;JEQ',
             '@SP', 'A=M-1', 'M=0', '@END.' + n,
             '0;JMP', '(EQ.true.' + n + ')', '@SP',
             'A=M-1', 'M=-1', '(END.' + n + ')']
        return s

    def LT(self):
        n = self.nextCount()
        s = ['//lt', '@SP', 'AM=M-1', 'D=M', 'A=A-1',
             'D=D-M', '@LT.true.' + n, 'D;JGT',
             '@SP', 'A=M-1', 'M=0', '@END.' + n,
             '0;JMP', '(LT.true.' + n + ')', '@SP',
             'A=M-1', 'M=-1', '(END.' + n + ')']
        return s

    def GT(self):
        n = self.nextCount()
        s = ['//gt', '@SP', 'AM=M-1', 'D=M', 'A=A-1',
             'D=D-M', '@GT.true.' + n, 'D;JLT',
             '@SP', 'A=M-1', 'M=0', '@END.' + n,
             '0;JMP', '(GT.true.' + n + ')', '@SP',
             'A=M-1', 'M=-1', '(END.' + n + ')']
        return s

    def IFGOTO(self, parse_line):
        loop_var = parse_line[1]
        s = ['@SP', 'AM=M-1', 'D=M', '@' + self.funcName + '$' + loop_var, 'D;JNE']
        return s

    def GOTO(self, parse_line):
        jmp_var = parse_line[1]
        s = ['@' + self.funcName + '$' + jmp_var, '0;JMP']
        return s

    def FUNCTION(self, parse_line):
        self.funcName = parse_line[1]
        s = ['(' + self.funcName + ')', '@SP', 'A=M']
        for i in range(int(parse_line[2])):
            s.extend(['M=0', 'A=A+1'])
        s.extend(['D=A', '@SP', 'M=D'])
        return s

    def CALL(self, parse_line):
        c = self.nextCount()
        s = ['@SP', 'D=M', '@R13', 'M=D', '//store return addr', '@RET.' + c, 'D=A',
             '@SP', 'A=M', 'M=D', '@SP', 'M=M+1', '//push LCL', '@LCL', 'D=M', '@SP',
             'A=M', 'M=D', '@SP', 'M=M+1', '//push ARG', '@ARG', 'D=M', '@SP', 'A=M', 'M=D',
             '@SP', 'M=M+1', '//push THIS', '@THIS', 'D=M', '@SP', 'A=M', 'M=D', '@SP',
             'M=M+1', '//push THAT', '@THAT', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1',
             '//ARG = R13 - nArgs', '@R13', 'D=M', '@' + parse_line[2], 'D=D-A', '@ARG', 'M=D',
             '//LCL = SP', '@SP', 'D=M', '@LCL', 'M=D', '@' + parse_line[1], '0;JMP', '(RET.' + c + ')']
        return s

    def parsePush(self, parse_line):
        ind = parse_line[2]
        if parse_line[1] == 'constant':
            return ['//push constant', '@' + ind, 'D=A', '@SP', 'AM=M+1', 'A=A-1', 'M=D']
        elif parse_line[1] == 'local':
            s = ['//push local', '@' + ind, 'D=A', '@LCL', 'A=M+D', 'D=M']
        elif parse_line[1] == 'argument':
            s = ['//push argument', '@' + ind, 'D=A', '@ARG', 'A=M+D', 'D=M']
        elif parse_line[1] == 'this':
            s = ['//push this', '@' + ind, 'D=A', '@THIS', 'A=M+D', 'D=M']
        elif parse_line[1] == 'that':
            s = ['//push that', '@' + ind, 'D=A', '@THAT', 'A=M+D', 'D=M']
        elif parse_line[1] == 'temp':
            s = ['//push temp', '@R5', 'D=A', '@' + ind, 'A=D+A', 'D=M']
        elif parse_line[1] == 'static':
            s = ['//push static', '@' + self.currfilename[:-3] + '.' + ind, 'D=M']
        elif parse_line[1] == 'pointer':
            if parse_line[2] == '0':
                s = ['//push pointer 0', '@THIS', 'D=M']
            else:
                s = ['//push pointer 1', '@THAT', 'D=M']
        s.extend(self.PUSH)
        return s

    def parsePop(self, parse_line):
        ind = parse_line[2]
        s = []
        if parse_line[1] == 'local':
            s = ['//pop local', '@LCL', 'D=M', '@' + ind, 'D=D+A']
        elif parse_line[1] == 'argument':
            s = ['//pop argument', '@ARG', 'D=M', '@' + ind, 'D=D+A']
        elif parse_line[1] == 'this':
            s = ['//pop this', '@THIS', 'D=M', '@' + ind, 'D=D+A']
        elif parse_line[1] == 'that':
            s = ['//pop that', '@THAT', 'D=M', '@' + ind, 'D=D+A']
        elif parse_line[1] == 'temp':
            s = ['//pop temp', '@R5', 'D=A', '@' + ind, 'D=D+A']
        elif parse_line[1] == 'static':
            s = ['//pop static', '@' + self.currfilename[:-3] + '.' + ind, 'D=A']
        elif parse_line[1] == 'pointer':
            if parse_line[2] == '0':
                s = ['//pop pointer 0', '@THIS', 'D=A']
            else:
                s = ['//pop pointer 1', '@THAT', 'D=A']
        s.extend(self.POP)
        return s

    def Parser(self, untranslated):
        # Removes whitespace and comments
        no_whitespace = []
        for line in untranslated:
            if '//' in line:
                comment_start = line.index('//')
                if comment_start == 0:
                    continue
                else:
                    line = line[:comment_start]
            if line == '\n':
                continue
            no_whitespace.append(line.strip())
        return no_whitespace

    def translate(self, vm_lines):
        translated = []
        for line in vm_lines:
            if line == 'add':
                translated.extend(self.ADD)
            elif line == 'sub':
                translated.extend(self.SUB)
            elif line == 'and':
                translated.extend(self.AND)
            elif line == 'or':
                translated.extend(self.OR)
            elif line == 'neg':
                translated.extend(self.NEG)
            elif line == 'not':
                translated.extend(self.NOT)
            elif line == 'eq':
                translated.extend(self.EQ())
            elif line == 'lt':
                translated.extend(self.LT())
            elif line == 'gt':
                translated.extend(self.GT())
            elif line == 'return':
                translated.extend(self.RETURN)
            else:
                split_line = line.split(' ')
                if split_line[0] == 'push':
                    translated.extend(self.parsePush(split_line))
                elif split_line[0] == 'pop':
                    translated.extend(self.parsePop(split_line))
                elif split_line[0] == 'label':
                    translated.append('(' + self.funcName + '$' + split_line[1] + ')')
                elif split_line[0] == 'if-goto':
                    translated.extend(self.IFGOTO(split_line))
                elif split_line[0] == 'goto':
                    translated.extend(self.GOTO(split_line))
                elif split_line[0] == 'function':
                    translated.extend(self.FUNCTION(split_line))
                elif split_line[0] == 'call':
                    translated.extend(self.CALL(split_line))

        return translated


# Main functionality
bootstrap = ['@Sys.init', '0;JMP']
trans = Translator()
# Open the .vm files and store each line in a list
for file in file_list:
    temp_vm_lines = []
    with open(join(dir_path, file), 'r') as vmfile:
        temp_vm_lines.extend(vmfile.readlines())
    trans.currfilename = file
    temp_vm_lines = trans.Parser(temp_vm_lines)
    bootstrap.extend(trans.translate(temp_vm_lines))

# Make or overwrite the .asm file with the translated asm lines
with open(dir_path + '\\' + dir_name + '.asm', 'w') as asmfile:
    asmfile.writelines('\n'.join(bootstrap))
