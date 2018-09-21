import sys

# Gets the file path from command line and also stores the dir and name of the file without the .asm extenstion
# That way the new .hack file is always in the same dir as the original file with the same name
file_path = sys.argv[1]
file_dir = file_path
file_dir = file_dir[::-1]
dir_index = file_dir.index('\\')
file_name = file_dir[3:dir_index]
file_dir = file_dir[dir_index:]
file_name = file_name[::-1]
file_dir = file_dir[::-1]

# Open the .vm file and store each line in a list
with open(file_path, 'r') as vmfile:
    vm_lines = vmfile.readlines()


class Translator():
    def __init__(self):
        self.count = 0
        self.ADD = ['//add', '@SP', 'AM=M-1', 'D=M', 'A=A-1', 'M=M+D']
        self.SUB = ['//sub', '@SP', 'AM=M-1', 'D=M', 'A=A-1', 'M=M-D']
        self.AND = ['//and', '@SP', 'AM=M-1', 'D=M', 'A=A-1', 'M=M&D']
        self.OR = ['//or', '@SP', 'AM=M-1', 'D=M', 'A=A-1', 'M=M|D']
        self.NEG = ['//neg', '@SP', 'A=M-1', 'M=-M']
        self.NOT = ['//not', '@SP', 'A=M-1', 'M=!M']
        self.POP = ['@R13', 'M=D', '@SP', 'AM=M-1', 'D=M', '@R13', 'A=M', 'M=D']
        self.PUSH = ['@SP', 'AM=M+1', 'A=A-1', 'M=D']

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
            s = ['//push static', '@static.' + ind, 'D=M']
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
            s = ['//pop static', '@static.' + ind, 'D=A']
        elif parse_line[1] == 'pointer':
            if parse_line[2] == '0':
                s = ['//pop pointer 0', '@THIS', 'D=M']
            else:
                s = ['pop pointer 1', '@THAT', 'D=M']
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
            else:
                split_line = line.split(' ')
                if split_line[0] == 'push':
                    translated.extend(self.parsePush(split_line))
                elif split_line[0] == 'pop':
                    translated.extend(self.parsePop(split_line))

        return translated


# Main functionality
bootstrap = ['@256', 'D=A', '@SP', 'M=D']
trans = Translator()
vm_lines_no_whitespace = trans.Parser(vm_lines)
del vm_lines
bootstrap.extend(trans.translate(vm_lines_no_whitespace))

# Make or overwrite the .asm file with the translated asm lines
with open(file_dir + file_name + '.asm', 'w') as asmfile:
    asmfile.writelines('\n'.join(bootstrap))
