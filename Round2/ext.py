#!/usr/bin/env python3

from pyshark import FileCapture

import pickle
import os
import glob
import random
import argparse
import collections
import time
time_stamp = str(int(time.time()))[-6:]

old_ctr = 0
new_ctr = 0

# list of *.pcap paths (recursively) inside root
# randomly choose num files if not None
def get_pcap_paths(root, num=None):
    paths = glob.glob(os.path.join(root, '**', '*.pcap'), recursive=True)
    #print(*paths, sep='\n')
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
    protocol_flows = collections.defaultdict(lambda: {
        'num pkts': 0,
        'first time': None,
        'last time': 0,
        'avg time': 0,
        'min len': float('inf'),
        'max len': 0,
        'sum len': 0,
        'avg len': 0,
        'first len': None,
        'last len': None,
        'out ratio': 0,
        'out len ratio': 0
    })

    pcap = FileCapture(pcap_path, only_summaries=True)

    freq = collections.defaultdict(int)
    for pkt in pcap:
        if pkt.source.find(':') != -1:
            continue
        if pkt.destination.find(':') != -1:
            continue
        freq[pkt.source] += 1
        freq[pkt.destination] += 1

    mx = 0
    for k, v in freq.items():
        if v > mx:
            mx = v
            host_ip = k
    #print('host_ip:', host_ip)

    for pkt in pcap:
        if pkt.source == host_ip:
            partner = pkt.destination
        elif pkt.destination == host_ip:
            partner = pkt.source
        else:
            continue # ff:ff:ff:ff:ff:ff type of src and dest
        d = protocol_flows[partner, pkt.protocol]
        d['num pkts'] += 1
        if d['first time'] == None:
            d['first time'] = float(pkt.time)
        d['last time'] = float(pkt.time)
        d['avg time'] += float(pkt.time)
        d['min len'] = min(d['min len'], float(pkt.length))
        d['max len'] = max(d['max len'], float(pkt.length))
        d['sum len'] += float(pkt.length)
        d['avg len'] += float(pkt.length)
        if d['first len'] == None:
            d['first len'] = float(pkt.length)
        d['last len'] = float(pkt.length)
        if pkt.source == host_ip:
            d['out ratio'] += 1
            d['out len ratio'] += float(pkt.length)

    flows = collections.defaultdict(dict)
    for (partner, protocol), d in protocol_flows.items():
        d['avg time'] /= d['num pkts']
        d['avg len'] /= d['num pkts']
        d['out ratio'] /= d['num pkts']
        d['out len ratio'] /= d['sum len']
        f = flows[partner]
        for k, v in d.items():
            f[protocol + '::' + k] = v

    return list(flows.values())

# get D (list of feature dicts), l (list of corresponding label strings) from a pcap file
# NOTE: again don't do low-level stuff here. Use LabelEncoder to get y (numerical label vector) from l
def get_D_l_single(pcap_path, only_outer_label=True, dump_root=None):
    global old_ctr, new_ctr
    g = os.path.join(dump_root, pcap_path.replace('/', '_').replace('\\', '_').replace('.', '_') + '_Dl_*.pickle')
    gl = glob.glob(g)
    if len(gl) != 0:
        gs = max(gl)
        print('loading existing pickle:', gs)
        D, l = pickle.load(open(gs, 'rb'))
        old_ctr += 1
        return D, l
    print('get_feature_dicts started at:', time.ctime())
    start = time.time()
    D = get_feature_dicts(pcap_path)
    finish = time.time()
    print('get_feature_dict time:', finish-start, 's')
    pcap, inner_class, outer_class = decompose_pcap_path(pcap_path)
    if only_outer_label:
        l = [outer_class for _ in range(len(D))]
    else:
        l = [outer_class + '::' + inner_class for _ in range(len(D))]
    if dump_root is not None:
        f = os.path.join(dump_root, pcap_path.replace('/', '_').replace('\\', '_').replace('.', '_') + '_Dl_' + time_stamp + '.pickle')
        pickle.dump((D, l), open(f, 'wb'))
        print("(D, l) dumped in:", f)
    new_ctr += 1
    return D, l

# get a combined D, l from all given paths
def get_D_l_many(pcap_paths, only_outer_label=True, dump_root=None):
    D = []
    l = []
    for pcap_path in pcap_paths:
        print("---")
        print("path:", pcap_path)
        D_, l_ = get_D_l_single(pcap_path, only_outer_label, dump_root)
        D += D_
        l += l_
        print('old:', old_ctr)
        print('new:', new_ctr)
        print('total:', old_ctr+new_ctr, '/', len(pcap_paths))
    return D, l

def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-r') # root directory to find pcaps in
    argparser.add_argument('-n', type=int) # number of pcaps to use
    argparser.add_argument('-p') # directory to dump pickles in, if not provided don't dump anything
    args = argparser.parse_args()
    D, l = get_D_l_many(get_pcap_paths(args.r, args.n), dump_root = args.p, only_outer_label=False)
    if args.p is not None:
        f = os.path.join(args.p, 'all_Dl_' + time_stamp + '.pickle')
        pickle.dump((D, l), open(f, 'wb'))

if __name__ == '__main__':
    main()
