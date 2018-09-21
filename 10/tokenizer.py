import sys
from os import listdir, makedirs
from os.path import isfile, join, isdir


class Tokenizer:
    # Tokenizer class funcitonality
    def __init__(self):
        self.keywords = {'class', 'method', 'function', 'constructor', 'int', 'boolean',
                         'char', 'void', 'var', 'static', 'field', 'let', 'do', 'if', 'else',
                         'while', 'return', 'true', 'false', 'null', 'this'}
        self.symbols = {'{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/',
                        '&', '|', '<', '>', '=', '~'}

    def isInt(self, num):
        for char in num:
            if char not in '0123456789':
                return False
        return True

    def parseLines(self, jack_lines):
        # Removes whitespace and comments
        no_whitespace = []
        comment = False
        for line in jack_lines:
            if comment:
                if '*/' in line:
                    comment = False
                continue

            if '//' in line:
                comment_start = line.index('//')
                if comment_start == 0:
                    continue
                else:
                    line = line[:comment_start]

            if '/*' in line:
                if '*/' not in line:
                    comment = True
                continue

            if not line.strip():
                continue
            no_whitespace.append(line.strip())
        return no_whitespace

    def translate(self, jack_lines):
        translated = []

        for line in jack_lines:
            translated.extend(self.translateLine(line))

        return translated

    def translateLine(self, jack_line):
        translated_line = []
        # Check for string constants in the line first
        if '"' in jack_line:
            temp = []
            while '"' in jack_line:
                str_start = jack_line.index('"')
                str_end = str_start + jack_line[str_start + 1:].index('"') + 1
                if jack_line[:str_start]:
                    temp.extend(jack_line[:str_start].split())
                # Include the first " so that the translator picks it up
                temp.append(jack_line[str_start:str_end])
                jack_line = jack_line[str_end + 1:]
            if jack_line:
                temp.extend(jack_line.split())
            jack_line = temp
        else:
            jack_line = jack_line.split()

        for item in jack_line:
            if item in self.keywords:
                translated_line.append('<keyword> ' + item + ' </keyword>')
            elif self.isInt(item):
                translated_line.append('<integerConstant> ' + item + ' </integerConstant>')
            elif item[0] == '"':
                translated_line.append('<stringConstant> ' + item[1:] + ' </stringConstant>')
            else:
                identifier = ''
                integer = ''
                for char in item:
                    if char in self.symbols:
                        if identifier or integer:
                            if identifier:
                                if identifier not in self.keywords:
                                    translated_line.append(
                                        '<identifier> ' + identifier + ' </identifier>')
                                    identifier = ''
                                else:
                                    translated_line.append(
                                        '<keyword> ' + identifier + ' </keyword>')
                                    identifier = ''
                            else:
                                translated_line.append(
                                    '<integerConstant> ' + integer + ' </integerConstant>')
                                integer = ''
                        if char != '<' and char != '>' and char != '"' and char != '&':
                            translated_line.append('<symbol> ' + char + ' </symbol>')
                        else:
                            if char == '<':
                                translated_line.append('<symbol> &lt; </symbol>')
                            elif char == '>':
                                translated_line.append('<symbol> &gt; </symbol>')
                            elif char == '"':
                                translated_line.append('<symbol> &quot; </symbol>')
                            else:
                                translated_line.append('<symbol> &amp; </symbol>')
                    elif self.isInt(char):
                        if not identifier:
                            integer = integer + char
                    else:
                        identifier = identifier + char
                if identifier:
                    if identifier not in self.keywords:
                        translated_line.append('<identifier> ' + identifier + ' </identifier>')
                    else:
                        translated_line.append('<keyword> ' + identifier + ' </keyword>')
                if integer:
                    translated_line.append('<integerConstant> ' + integer + ' </integerConstant>')

        return translated_line


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
        tokens.insert(0, '<tokens>')
        tokens.append('</tokens>')
        if not isdir(dir_path[:-len(dir_name)] + '\\my' + dir_name):
            makedirs(dir_path[:-len(dir_name)] + '\\my' + dir_name)
        with open(dir_path[:-len(dir_name)] + '\\my' + dir_name + '\\' + file[:-5] + '.xml', 'w') as xml_file:
            xml_file.writelines('\n'.join(tokens))
