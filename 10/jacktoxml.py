import sys
from tokenizer import Tokenizer
from os import listdir, makedirs
from os.path import isfile, join, isdir


class jackToXml():
    def __init__(self):
        self.index = 0
        self.tab_count = 0
        self.token_list = []
        self.statements = {'let', 'if', 'while', 'do', 'return'}
        self.subroutines = {'method', 'constructor', 'function'}
        self.ops = {'+', '-', '*', '/', '&amp', '|', '&lt', '&gt', '='}
        self.expression_terminators = {',', ')', ']', ';'}

    def advance(self):
        self.index += 1
        return

    def add_explicit_symbols(self, num):
        temp_list = []
        for i in range(num):
            temp_list.append(self.token_list[self.index])
            self.advance()

        return temp_list

    def compiler(self, token_list):
        self.token_list = token_list
        compiled_tokens = []
        while self.index < len(token_list):
            compiled_tokens.extend(self.compileClass())

        return compiled_tokens

    def compileClass(self):
        temp_list = ['<class>']
        temp_list.extend('\t' + char for char in self.add_explicit_symbols(3)
                         )  # Keyword class, Identifier, and Symbol {
        while self.token_list[self.index].split()[1] == 'field' or self.token_list[self.index].split()[1] == 'static':
            temp_list.extend('\t' + char for char in self.compileClassVarDec())

        while self.token_list[self.index].split()[1] in self.subroutines:
            temp_list.extend('\t' + char for char in self.compileSubroutine())

        temp_list.extend('\t' + char for char in self.add_explicit_symbols(1))  # Symbol }
        temp_list.append('</class>')
        return temp_list

    def compileClassVarDec(self):
        temp_list = ['<classVarDec>']
    # while self.token_list[self.index].split()[1] not in self.statements: # NOTE: Not sure why this was here
        while self.token_list[self.index].split()[1] != ';':
            temp_list.extend('\t' + char for char in self.add_explicit_symbols(1))
        temp_list.extend('\t' + char for char in self.add_explicit_symbols(1))  # Symbol ;
        temp_list.append('</classVarDec>')

        return temp_list

    def compileVarDec(self):
        temp_list = ['<varDec>']
        while self.token_list[self.index].split()[1] != ';':
            temp_list.extend('\t' + char for char in self.add_explicit_symbols(1))
        temp_list.extend('\t' + char for char in self.add_explicit_symbols(1))  # Symbol ;
        temp_list.append('</varDec>')

        return temp_list

    def compileSubroutine(self):
        temp_list = ['<subroutineDec>']
        while self.token_list[self.index].split()[1] != '(':
            temp_list.extend('\t' + char for char in self.add_explicit_symbols(1))
        temp_list.extend('\t' + char for char in self.add_explicit_symbols(1))  # Symbol (
        # Subroutine parameters
        temp_list.extend('\t' + char for char in self.compileParameterList())
        temp_list.extend('\t' + char for char in self.add_explicit_symbols(1))  # Symbol )
        # Subroutine Body
        temp_list.append('\t<subroutineBody>')
        temp_list.extend('\t\t' + char for char in self.add_explicit_symbols(1))  # Symbol {
        while self.token_list[self.index].split()[1] == 'var':
            temp_list.extend('\t\t' + char for char in self.compileVarDec())
        temp_list.extend('\t\t' + char for char in self.compileStatements())
        temp_list.extend('\t\t' + char for char in self.add_explicit_symbols(1))  # Symbol }
        temp_list.extend(['\t</subroutineBody>', '</subroutineDec>'])

        return temp_list

    def compileParameterList(self):
        temp_list = ['<parameterList>']
        while self.token_list[self.index].split()[1] != ')':
            temp_list.extend('\t' + char for char in self.add_explicit_symbols(1))
        temp_list.append('</parameterList>')

        return temp_list

    def compileStatements(self):
        temp_list = ['<statements>']
        while self.token_list[self.index].split()[1] in self.statements:
            _statement = self.token_list[self.index].split()[1]

            if _statement == 'do':
                temp_list.extend('\t' + char for char in self.compileDo())
            elif _statement == 'let':
                temp_list.extend('\t' + char for char in self.compileLet())
            elif _statement == 'while':
                temp_list.extend('\t' + char for char in self.compileWhile())
            elif _statement == 'return':
                temp_list.extend('\t' + char for char in self.compileReturn())
            elif _statement == 'if':
                temp_list.extend('\t' + char for char in self.compileIf())
        temp_list.append('</statements>')

        return temp_list

    def compileDo(self):
        temp_list = ['<doStatement>']
        temp_list.extend('\t' + char for char in self.add_explicit_symbols(1))  # Keyword do
        while self.token_list[self.index].split()[1] != '(':
            temp_list.extend('\t' + char for char in self.add_explicit_symbols(1))
        temp_list.extend('\t' + char for char in self.add_explicit_symbols(1))  # Symbol (
        temp_list.extend('\t' + char for char in self.compileExpressionList())
        temp_list.extend('\t' + char for char in self.add_explicit_symbols(2))  # Symbols ) and ;
        temp_list.append('</doStatement>')

        return temp_list

    def compileLet(self):
        temp_list = ['<letStatement>']
        temp_list.extend('\t' + char for char in self.add_explicit_symbols(2)
                         )  # Keyword let and identifier
        if self.token_list[self.index].split()[1] == '[':
            temp_list.extend('\t' + char for char in self.add_explicit_symbols(1))  # Symbol [

            temp_list.extend('\t' + char for char in self.compileExpression())

            temp_list.extend('\t' + char for char in self.add_explicit_symbols(1))  # Symbol ]

        temp_list.extend('\t' + char for char in self.add_explicit_symbols(1))  # Symbol =
        temp_list.extend('\t' + char for char in self.compileExpression())
        temp_list.extend('\t' + char for char in self.add_explicit_symbols(1))  # Symbol ;
        temp_list.append('</letStatement>')

        return temp_list

    def compileWhile(self):
        temp_list = ['<whileStatement>']
        temp_list.extend('\t' + char for char in self.add_explicit_symbols(2)
                         )  # Keyword while and Symbol (
        temp_list.extend('\t' + char for char in self.compileExpression())
        temp_list.extend('\t' + char for char in self.add_explicit_symbols(2))  # Symbol ) and {
        temp_list.extend('\t' + char for char in self.compileStatements())
        temp_list.extend('\t' + char for char in self.add_explicit_symbols(1))  # Symbol }
        temp_list.append('</whileStatement>')

        return temp_list

    def compileReturn(self):
        temp_list = ['<returnStatement>']
        temp_list.extend('\t' + char for char in self.add_explicit_symbols(1))  # Keyword return
        if self.token_list[self.index].split()[1] != ';':
            temp_list.extend('\t' + char for char in self.compileExpression())
        temp_list.extend('\t' + char for char in self.add_explicit_symbols(1))  # Symbol ;
        temp_list.append('</returnStatement>')

        return temp_list

    def compileIf(self):
        temp_list = ['<ifStatement>']
        temp_list.extend('\t' + char for char in self.add_explicit_symbols(2)
                         )  # Keyword if and Symbol (
        temp_list.extend('\t' + char for char in self.compileExpression())
        temp_list.extend('\t' + char for char in self.add_explicit_symbols(2))  # Symbol ) and {
        temp_list.extend('\t' + char for char in self.compileStatements())
        temp_list.extend('\t' + char for char in self.add_explicit_symbols(1))  # Symbol }
        if self.token_list[self.index].split()[1] == 'else':
            temp_list.extend('\t' + char for char in self.add_explicit_symbols(2)
                             )  # Keyword else and Symbol {
            temp_list.extend('\t' + char for char in self.compileStatements())
            temp_list.extend('\t' + char for char in self.add_explicit_symbols(1))  # Symbol }
        temp_list.append('</ifStatement>')

        return temp_list

    def compileExpression(self):
        temp_list = ['<expression>']
        temp_list.extend('\t' + char for char in self.compileTerm())

        while self.token_list[self.index].split()[1] not in self.expression_terminators:
            temp_list.extend('\t' + char for char in self.add_explicit_symbols(1))  # Operator
            temp_list.extend('\t' + char for char in self.compileTerm())

        temp_list.append('</expression>')

        return temp_list

    def compileExpressionList(self):
        temp_list = ['<expressionList>']

        while self.token_list[self.index].split()[1] != ')':
            temp_list.extend('\t' + char for char in self.compileExpression())
            if self.token_list[self.index].split()[1] == ',':
                temp_list.extend('\t' + char for char in self.add_explicit_symbols(1))  # Symbol ,

        temp_list.append('</expressionList>')

        return temp_list

    def compileTerm(self):
        temp_list = ['<term>']
        term = self.token_list[self.index].split()
        if term[1] == '(':
            temp_list.extend('\t' + char for char in self.add_explicit_symbols(1))  # Symbol (
            temp_list.extend('\t' + char for char in self.compileExpression())
            temp_list.extend('\t' + char for char in self.add_explicit_symbols(1))  # Symbol )
        elif term[1] == '-' or term[1] == '~':
            temp_list.extend('\t' + char for char in self.add_explicit_symbols(1)
                             )  # Symbol ~ or Symbol -
            temp_list.extend('\t' + char for char in self.compileTerm())
        elif term[0] == '<identifier>':
            if self.token_list[self.index + 1].split()[1] == '(' or self.token_list[self.index + 1].split()[1] == '.':
                while self.token_list[self.index].split()[1] != '(':
                    temp_list.extend('\t' + char for char in self.add_explicit_symbols(1))
                temp_list.extend('\t' + char for char in self.add_explicit_symbols(1))  # Symbol (
                temp_list.extend('\t' + char for char in self.compileExpressionList())
                temp_list.extend('\t' + char for char in self.add_explicit_symbols(1))  # Symbol )
            elif self.token_list[self.index + 1].split()[1] == '[':
                temp_list.extend('\t' + char for char in self.add_explicit_symbols(2)
                                 )  # varName Identifier and Symbol [
                temp_list.extend('\t' + char for char in self.compileExpression())
                temp_list.extend('\t' + char for char in self.add_explicit_symbols(1))  # Symbol ]
            else:
                temp_list.extend('\t' + char for char in self.add_explicit_symbols(1))
        else:
            temp_list.extend('\t' + char for char in self.add_explicit_symbols(1))
        temp_list.append('</term>')

        return temp_list


if __name__ == '__main__':
    # Gets the dir path from command line and name of all files with the .vm extenstion
    # The new .asm file will be in the same dir with the dir name
    dir_path = sys.argv[1]
    file_list = []
    for file in listdir(dir_path):
        if file[-5:] == '.jack':
            file_list.append(file)
    dir_path = dir_path[::-1]
    dir_index = dir_path.index('\\')
    dir_name = dir_path[:dir_index]
    dir_name = dir_name[::-1]
    dir_path = dir_path[::-1]

    # Main functionality
    tokenizer = Tokenizer()

    for file in file_list:
        tokens = []
        with open(join(dir_path, file), 'r') as jack_file:
            tokens.extend(jack_file.readlines())

        tokens = tokenizer.parseLines(tokens)
        tokens = tokenizer.translate(tokens)

        parser = jackToXml()
        jack_to_xml = parser.compiler(tokens)

        if not isdir(dir_path[:-len(dir_name)] + '\\my' + dir_name):
            makedirs(dir_path[:-len(dir_name)] + '\\my' + dir_name)
        with open(dir_path[:-len(dir_name)] + '\\my' + dir_name + '\\' + file[:-5] + '.xml', 'w') as xml_file:
            xml_file.writelines('\n'.join(jack_to_xml))
