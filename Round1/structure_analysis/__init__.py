# parser for Structure_Info.txt files
# author: Rishabh Ranjan
#
# i'm calling sections and headers ('---...---' and '[...]') as contexts (ctx)
# every context is given a unique name (heading, unique id among headings)
# useful info is available in:
# 1. ctx_dict: a dict from context name to a dict of feature names and values
# 2. ctx_aux: a dict from context name to a list of non-feature lines in the context
# 3. ctx_children: a dict from context name to a list of names of its children contexts

import sys

class Parser:

    lines = None
    ctx_name_ctr = {}
    curr_ctx_name = None
    ctx_dict = {}
    ctx_aux = {}
    ctx_children = {}

    def __init__(self, lines):
        self.lines = lines

    def is_h1(l):
        return len(l) != 0 and l[0] == '-'

    def is_h2(l):
        return len(l.lstrip()) != 0 and l.lstrip()[0] == '['

    def is_new_ctx(l):
        return Parser.is_h1(l) or Parser.is_h2(l)

    def name_new_ctx(self, l):
        l = l.strip();
        if l in self.ctx_name_ctr:
            self.ctx_name_ctr[l] += 1
        else:
            self.ctx_name_ctr[l] = 0;
        return (l, self.ctx_name_ctr[l])

    def is_kv_pair(l):
        return l.find(':') != -1

    def get_kv_pair(l):
        t = l.split(':')
        if len(t) < 2:
            t.append('0x0')
        t[0] = t[0].strip()
        t[1] = t[1].strip()
        if t[0][:2] == '0x':
            t[0] = t[0].split(' ')[-1]
        if t[1][:2] == '0x':
            t[1] = t[1].split(' ')[0]
            t[1] = int(t[1], 16)
        if t[0] == 'Entropy':
            t[1] = t[1].split(' ')[0]
            t[1] = float(t[1])
        return t

    def parse_inner(self):
        self.ctx_name_ctr = {}
        self.curr_ctx_name = None
        for l in self.lines:
            if Parser.is_new_ctx(l):
                self.curr_ctx_name = self.name_new_ctx(l)
                self.ctx_dict[self.curr_ctx_name] = {}
                self.ctx_aux[self.curr_ctx_name] = []
            else:
                if Parser.is_kv_pair(l):
                    kv = Parser.get_kv_pair(l)
                    if type(kv[1]) == str and kv[1].find(',') != -1:
                        toks = kv[1].split(',')
                        toks = [t.strip() for t in toks]
                        for t in toks:
                            self.ctx_dict[self.curr_ctx_name][kv[0] + '::' + t] = 1
                    else:
                        self.ctx_dict[self.curr_ctx_name][kv[0]] = kv[1]
                else:
                    self.ctx_aux[self.curr_ctx_name].append(l.strip())

    def parse_outer_h1(self):
        self.ctx_name_ctr = {}
        self.curr_ctx_name = None
        for l in self.lines:
            if Parser.is_new_ctx(l):
                tmp = self.name_new_ctx(l)
            if Parser.is_h1(l):
                self.curr_ctx_name = tmp
                self.ctx_children[self.curr_ctx_name] = []
            elif Parser.is_h2(l):
                self.ctx_children[self.curr_ctx_name].append(tmp)

    def get_indent(l):
        return len(l) - len(l.lstrip())

    def parse_outer_h2(self, indent):
        self.ctx_name_ctr = {}
        self.curr_ctx_name = None
        flag = False
        for l in self.lines:
            if Parser.is_new_ctx(l):
                tmp = self.name_new_ctx(l)
            if Parser.is_h2(l) and Parser.get_indent(l) == indent:
                self.curr_ctx_name = tmp
                self.ctx_children[self.curr_ctx_name] = []
            elif Parser.is_h2(l) and Parser.get_indent(l) == indent+1:
                self.ctx_children[self.curr_ctx_name].append(tmp)
                flag = True
        return flag

    def parse_outer(self):
        self.parse_outer_h1()
        indent = 0
        while self.parse_outer_h2(indent):
            indent += 1

    def parse(self):
        # order doesn't matter
        self.parse_inner()
        self.parse_outer()

# TODO:
# 1. derived features from dos_header: size of e_res and e_res2
# 3. avg section depth for resources
# 8. ensure that min and max tokens specified for entropy are same everywhere
# 9. number of sections could be a useful feature - like relative number of text, CODE, etc sections
# 10. give dict strings to aux_dump, then do string analysis on aux_dump

def extract_features(p):
    ret = {}
    rep_ctr = {}
    rep_sum = {}
    rep_max = {}
    rep_min = {}
    for k, v in p.ctx_dict.items():
        gname = k[0]
        for fk, fv in v.items():
            if fk == 'Name' and type(fv) == str:
                gname += '::' + fk + '=' + fv
        for fk, fv in v.items():
            if type(fv) == str:
                continue
            name = gname + '::' + fk
            if name in ret:
                ret[name] = fv
                rep_ctr[name] += 1
                rep_sum[name] += fv
                rep_max[name] = max(rep_max[name], fv)
                rep_min[name] = min(rep_min[name], fv)
            else:
                rep_ctr[name] = 1
                rep_sum[name] = fv
                rep_max[name] = fv
                rep_min[name] = fv
    for k, v in rep_ctr.items():
        if v == 1:
            ret[k] = rep_sum[k]
        else:
            ret[k + '::mean'] = rep_sum[k] / rep_ctr[k]
            ret[k + '::max'] = rep_max[k]
            ret[k + '::min'] = rep_min[k]
    dll_ctr = {}
    for k, v in p.ctx_aux.items():
        for l in v:
            if l.find('dll') != -1:
                dll_str = k[0] + '::' + l.split('.')[0] + '.dll'
                if dll_str in dll_ctr:
                    dll_ctr[dll_str] += 1
                else:
                    dll_ctr[dll_str] = 1
    for k, v in dll_ctr.items():
        ret[k] = v
    return ret

def aux_dump(parser):
    for k, v in parser.ctx_aux.items():
        if len(v) != 0:
            print(*v, sep = '\n')

def get_feature_dict(filename):
    lines = open(filename + '/Structure_Info.txt', 'r')
    lines = [l.rstrip() for l in lines if l.rstrip()]
    parser = Parser(lines)
    parser.parse()
    return extract_features(parser)

def main():
    lines = sys.stdin.readlines()
    lines = [l.rstrip() for l in lines if l.rstrip()]
    # print(*lines, sep='\n')
    parser = Parser(lines)
    parser.parse()
    print("=== ctx_dict ===")
    print(*parser.ctx_dict.items(), sep = '\n')
    print()
    print()
    print("=== ctx_aux ===")
    print(*parser.ctx_aux.items(), sep = '\n')
    print()
    print()
    print("=== ctx_children ===")
    print(*parser.ctx_children.items(), sep = '\n')
    print()
    print()
    print("=== ctx_name_ctr ===")
    print(*parser.ctx_name_ctr.items(), sep = '\n')
    print()
    print()
    print("=== features ===")
    print(*extract_features(parser).items(), sep = '\n')
    print()
    print()
    print("=== aux_dump ===")
    aux_dump(parser)

if __name__ == '__main__':
    main()
    #print(get_feature_dict('../static_samples/benign/00b39e152ec2f569424596049b35917c7b767b16132f63a0330ccc3b89c7f188'))
