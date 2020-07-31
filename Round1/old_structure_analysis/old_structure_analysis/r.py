#TODO: make it robust so that it never throws error on new files

import sys

def is_mem(line):
    return line[:2] == '0x'

def parse_mem(line):
    tokens = line.split(' ')
    tokens = [t for t in tokens if t != '']
    if (len(tokens) < 4):
        return [tokens[2], '0x0'] #TODO: giving 0 for unknow vals... ok?
    return [tokens[2], tokens[3]]

def is_list(token):
    return token.find(',') != -1

def parse_list(token):
    tokens = token.split(',')
    for i in range(len(tokens)):
        if tokens[i][0] == ' ':
            tokens[i] = tokens[i][1:]
    return tokens

def is_info(line):
    return line.find(':') != -1

def parse_info(line):
    t = line.split(':')
    assert len(t) == 2
    t[1] = t[1][1:]
    if is_list(t[1]):
        t[1] = parse_list(t[1])
    return [t[0], t[1]]

def parse_line(line):
    if is_mem(line):
        return parse_mem(line)
    elif is_info(line):
        return parse_info(line)
    else:
        return line

def remove_indent(lines):
    return [line[2:] for line in lines]

def parse_secondary(lines):
    ret = [['', []]]
    for line in lines:
        if line[0] == '[':
            if len(ret[-1][1]) != 0:
                inner = ret[-1][1]
                iret = []
                indented = []
                for iline in inner:
                    if (iline[0] == ' '):
                        indented.append(iline)
                    else:
                        if len(indented) != 0:
                            iret.append(parse_secondary(remove_indent(indented)))
                        iret.append(parse_line(iline))
                if (len(indented) != 0):
                    iret.append(parse_secondary(remove_indent(indented)))
                ret[-1][1] = iret
            ret.append([line, []])
        else:
            ret[-1][1].append(line)
    if len(ret[-1][1]) != 0:
        inner = ret[-1][1]
        iret = []
        indented = []
        for iline in inner:
            if (iline[0] == ' '):
                indented.append(iline)
            else:
                if len(indented) != 0:
                    iret.append(parse_secondary(remove_indent(indented)))
                iret.append(parse_line(iline))
        if (len(indented) != 0):
            iret.append(parse_secondary(remove_indent(indented)))
        ret[-1][1] = iret
    if len(ret[0][1]) != 0:
        return ret[0][1] + ret[1:]
    else:
        return ret[1:]
#    ret = []
#    indented = []
#    for line in lines:
#        if line[0] == ' ':
#            indented.append(line)
#        else:
#            if len(indented) != 0:
#                ret.append(parse_secondary(remove_indent(indented)))
#            ret.append(parse_line(line))
#    if (len(indented) != 0):
#        ret.append(parse_secondary(remove_indent(indented)))
#    return ret

# remove empty lines first
def parse_primary(lines):
    ret = [['', []]]
    for line in lines:
        if line[0] == '-':
            ret.append([line, []])
        else:
            ret[-1][1].append(line)
    for i in range(len(ret)):
        ret[i][1] = parse_secondary(ret[i][1])
    if len(ret[0][1]) != 0:
        return ret[0][1] + ret[1:]
    else:
        return ret[1:]

def main():
    f = open(sys.argv[1], 'r')
    s = f.read();
    l = s.split('\n');
    l = [x for x in l if x != '']
    obj = parse_primary(l)
    print(obj)

main()
