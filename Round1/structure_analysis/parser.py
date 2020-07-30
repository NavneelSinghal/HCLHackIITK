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
# 2. comma separated flags
# 3. entropy

def extract_features(p):
    ret = {}
    rep_ctr = {}
    rep_sum = {}
    rep_max = {}
    rep_min = {}
    for k, v in p.ctx_dict.items():
        if p.ctx_name_ctr[k[0]] == 0:
            for fk, fv in v.items():
                ret[k[0] + '::' + fk] = fv
        else:
            for fk, fv in v.items():
                if type(fv) == str:
                    continue
                name = k[0] + '::' + fk
                if name in rep_ctr:
                    rep_ctr[name] += 1
                else:
                    rep_ctr[name] = 1
                if name in rep_sum:
                    rep_sum[name] += fv
                else:
                    rep_sum[name] = 1
                if name in rep_max:
                    rep_max[name] = max(rep_max[name], fv)
                else:
                    rep_max[name] = fv
                if name in rep_min:
                    rep_min[name] = min(rep_max[name], fv)
                else:
                    rep_min[name] = fv
    for k in rep_ctr.keys():
        ret[k + '::mean'] = rep_sum[k] / rep_ctr[k]
        ret[k + '::max'] = rep_max[k]
        ret[k + '::min'] = rep_min[k]
    return ret

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

if __name__ == '__main__':
    main()
