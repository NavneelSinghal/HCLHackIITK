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
        t[0] = t[0].split(' ')[-1]
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

def main():
    lines = sys.stdin.readlines()
    lines = [l.rstrip() for l in lines if l.rstrip()]
    # print(*lines, sep='\n')
    parser = Parser(lines)
    parser.parse()
    print("=== ctx_dict ===")
    print(parser.ctx_dict)
    print()
    print()
    print("=== ctx_aux ===")
    print(parser.ctx_aux)
    print()
    print()
    print("=== ctx_children ===")
    print(parser.ctx_children)
    print()
    print()

if __name__ == '__main__':
    main()
