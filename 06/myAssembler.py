import sys

# Gets the file path from command line and also stores the dir and name of the file without the .asm extenstion
# That way the new .hack file is always in the same dir as the original file with the same name
file_path = sys.argv[1]
file_dir = file_path
file_dir = file_dir[::-1]
dir_index = file_dir.index('\\')
file_name = file_dir[4:dir_index]
file_dir = file_dir[dir_index:]
file_name = file_name[::-1]
file_dir = file_dir[::-1]

# predefined keywords and mem addresses
symbol_dict = {'R0': 0, 'R1': 1, 'R2': 2, 'R3': 3, 'R4': 4, 'R5': 5, 'R6': 6, 'R7': 7, 'R8': 8, 'R9': 9,
               'R10': 10, 'R11': 11, 'R12': 12, 'R13': 13, 'R14': 14, 'R15': 15, 'SCREEN': 16384, 'KBD': 24576,
               'SP': 0, 'LCL': 1, 'ARG': 2, 'THIS': 3, 'THAT': 4}

jmp_cases = {'JGT': '001', 'JEQ': '010', 'JGE': '011',
             'JLT': '100', 'JNE': '101', 'JLE': '110', 'JMP': '111'}

dest_cases = {'M': '001', 'D': '010', 'A': '100',
              'MD': '011', 'AD': '110', 'AM': '101', 'AMD': '111'}

comp_cases = {'0': '101010', '1': '111111', '-1': '111010', 'D': '001100', 'A': '110000', '!D': '001101',
              '!A': '110001', '-D': '001101', '-A': '110011', 'D+1': '011111', 'A+1': '110111',
              'D-1': '011111', 'A-1': '110010', 'D+A': '000010', 'D-A': '010011', 'A-D': '000111',
              'D&A': '000000', 'D|A': '010101'}
# Open the .asm file and store each line in a list
with open(file_path, 'r') as asmfile:
    asm_lines = asmfile.readlines()


def toBinary(num):
    binary = ''
    while(num != 0):
        binary = str(num % 2) + binary
        num = num // 2
    while len(binary) < 16:
        binary = '0' + binary

    return binary


def Parser(untranslated):
    # Removes whitespace and comments
    nowhitespace = []
    for line in untranslated:
        if '//' in line:
            comment_start = line.index('//')
            if comment_start == 0:
                continue
            else:
                line = line[:comment_start]
        if line == '\n':
            continue
        nowhitespace.append(line.strip())
    return nowhitespace


def symbolTrans(lst):
    # First Give L Commands Address according to their line in the program
    parencounter = 0
    for i, line in enumerate(lst):
        if line[0] == '(':
            if isNumeric([line[1:-1]]):
                continue
            elif line[1:-1] not in symbol_dict:
                symbol_dict[line[1:-1]] = i - parencounter
                parencounter += 1

    # Then translate all A and L commands into their binary equivalent
    memindex = 16
    binarylist = []
    for j, line in enumerate(lst):
        if line[0] == '@':
            if isNumeric(line[1:]):
                binarylist.append('@' + toBinary(int(line[1:])))
            elif line[1:] not in symbol_dict:
                while(memindex in symbol_dict.values()):
                    memindex += 1
                symbol_dict[line[1:]] = memindex
                binarylist.append('@' + toBinary(memindex))
                memindex += 1
            else:
                binarylist.append('@' + toBinary(symbol_dict[line[1:]]))

        elif line[0] == '(':
            continue
        else:
            binarylist.append(line)

    return binarylist


def Translate(lst):
    # Translates line according to command type
    for i, line in enumerate(lst):
        if line[0] == '@':
            lst[i] = line[1:]

        elif line[0] == '(':
            lst[i] = line[1:-1]

        else:
            lst[i] = CCommand(line)


def isNumeric(str):
    for char in str:
        if char not in '0123456789':
            return False
    return True


def CCommand(cline):
    binary = '111'
    if '=' in cline:
        eqindex = cline.index('=')
        deststr = dest_cases[cline[:eqindex]]
        compstr = cline[eqindex + 1:]
        jmpstr = '000'
        if 'M' in compstr:
            a = '1'
            Mindex = compstr.index('M')
            compstr = compstr[: Mindex] + 'A' + compstr[Mindex + 1:]
        else:
            a = '0'
        compstr = comp_cases[compstr]

    elif ';' in cline:
        scindex = cline.index(';')
        deststr = '000'
        jmpstr = jmp_cases[cline[scindex + 1:]]
        cond = cline[: scindex]
        if cond == 'M':
            a = '1'
            cond = 'A'
        else:
            a = '0'
        compstr = comp_cases[cond]

    return binary + a + compstr + deststr + jmpstr


# Main program flow
hack_lines = Parser(asm_lines)
hack_lines = symbolTrans(hack_lines)
Translate(hack_lines)

# Make or overwrite the .hack file with the translated binary lines
with open(file_dir + file_name + '.hack', 'w') as hackfile:
    hackfile.writelines('\n'.join(hack_lines))
