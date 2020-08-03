#!/usr/bin/env python3

# TODO:
# 1. how to get whether packet is incoming or outgoing?
# 2. [Raw] layer is not available in a lot of pkts, what are these packets? which sessions do they belong to? what to do about them?
# 3. sometimes there are out of index errors, look and fix (if required)

from scapy.all import *

import pickle
import os
import glob
import random
import argparse

# list of *.pcap paths (recursively) inside root
# randomly choose num files if not None
def get_pcap_paths(root, num=None):
    paths = glob.glob(os.path.join(root, '**', '*.pcap'), recursive=True)
    print(*paths, sep='\n')
    print("number of pcaps detected:", len(paths))
    if num is None:
        return paths
    else:
        random.shuffle(paths)
        return paths[:num]

# return pcap name, inner class name and outer class name from a pcap path
def decompose_pcap_path(path):
    h, t = os.path.split(path)
    pcap = t
    try:
        hh, ht = os.path.split(h)
        inner_class = ht
        try:
            _, hht = os.path.split(hh)
            outer_class = hht
        except:
            outer_class = None
    except:
        inner_class = None
    return pcap, inner_class, outer_class

# list of feature dicts extracted from the pcap file
# NOTE: don't try to do low level stuff here. use DictVectorizer to get the feature matrix
def get_feature_dicts(pcap_path):
    print('reading pcap...')
    pcap = rdpcap(pcap_path)
    ret = []
    ctr = 0
    for head, pkts in pcap.sessions().items():
        print(ctr, end='\r')
        ctr += 1
        try:
            fdict = {}
            toks = head.split(' ')
            src_ip = toks[1].split(':')[0]
            fdict['protocol'] = toks[0]
            fdict['src ip'] = toks[1].split(':')[0]
            fdict['src port'] = toks[1].split(':')[1]
            fdict['dest ip'] = toks[3].split(':')[0]
            fdict['dest port'] = toks[3].split(':')[1]
            fdict['len of first pkt'] = len(pkts[0])
            fdict['total pkts'] = len(pkts)
            a_len = 0
            a_load = 0
            a_out = 0
            for pkt in pkts:
                a_len += len(pkt)
                a_load += len(pkt[Raw])
                if pkt[IP].src == toks[0]:
                    a_out += 1
            fdict['total bytes'] = a_load
            fdict['avg bytes'] = a_load / len(pkts)
            fdict['avg pkt len'] = a_len / len(pkts)
            # these don't work as of now
            #fdict['in ratio'] = (len(pkts) - a_out) / len(pkts)
            #fdict['out ratio'] = a_out / len(pkts)
            ret.append(fdict)
        except Exception as err:
            print(err)
            #input()
    print()
    return ret

# get D (list of feature dicts), l (list of corresponding label strings) from a pcap file
# NOTE: again don't do low-level stuff here. Use LabelEncoder to get y (numerical label vector) from l
def get_D_l_single(pcap_path, only_outer_label=True, dump_root=None):
    D = get_feature_dicts(pcap_path)
    pcap, inner_class, outer_class = decompose_pcap_path(pcap_path)
    if only_outer_label:
        l = [outer_class for _ in range(len(D))]
    else:
        l = [outer_class + '::' + inner_class for _ in range(len(D))]
    if dump_root is not None:
        f = os.path.join(dump_root, pcap_path.replace('/', '_').replace('\\', '_').replace('.', '_') + '_Dl.pickle')
        pickle.dump((D, l), open(f, 'wb'))
        print("(D, l) dumped in:", f)
    return D, l

# get a combined D, l from all given paths
def get_D_l_many(pcap_paths, only_outer_label=True, dump_root=None):
    D = []
    l = []
    for pcap_path in pcap_paths:
        print("path:", pcap_path)
        D_, l_ = get_D_l_single(pcap_path, only_outer_label, dump_root)
        D += D_
        l += l_
    return D, l

def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-r') # root directory to find pcaps in
    argparser.add_argument('-n', type=int) # number of pcaps to use
    argparser.add_argument('-p') # directory to dump pickles in, if not provided don't dump anything
    args = argparser.parse_args()
    D, l = get_D_l_many(get_pcap_paths(args.r, args.n), dump_root = args.p)
    if args.p is not None:
        f = os.path.join(args.p, 'all_Dl.pickle')
        pickle.dump((D, l), open(f, 'wb'))

if __name__ == '__main__':
    main()
