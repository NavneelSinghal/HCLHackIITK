import collections
import glob
import math
import os
import pickle
import subprocess
import time

def get_dns_ips(pcap_path):
    proc = subprocess.Popen(
        ['tshark', '-r', pcap_path, '-Y', 'dns && dns.flags.response == 1', '-T', 'fields', '-e', 'dns.a'],
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        universal_newlines = True
    )
    # print errs to a file to see error output
    outs, errs = proc.communicate()
    lines = [l for l in outs.split('\n') if l.rstrip()]
    ret = []
    for l in lines:
        ret += l.split(',')
    return ret

def calc_feature_dict(pcap_path, ignore_protocols=False):
    dns_ips = set(get_dns_ips(pcap_path))
    proc = subprocess.Popen(
        ['tshark', '-r', pcap_path],
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        universal_newlines = True
        )
    outs, errs = proc.communicate()
    lines = outs.split('\n')
    flows = collections.defaultdict(lambda: (collections.defaultdict(float), collections.defaultdict(float)))

    for l in lines:
        try:
            l = l.split(' ')
            l = [x for x in l if x != '']
            ptime = float(l[1])
            src = l[2]
            dest = l[4]
            if src in dns_ips or dest in dns_ips:
                continue
            proto = l[5]
            ind = 6
            while True:
                try:
                    plen = int(l[ind])
                    break
                except ValueError:
                    proto += '_' + l[ind]
                    ind += 1
                except:
                    break
        except:
            continue
        ip1, ip2 = sorted([src, dest])
        d, dd = flows[ip1, ip2]
        if ignore_protocols:
            s = '_#'
        else:
            s = proto+'#'
        d[s+'num_pkts'] += 1
        if dd[s+'first_time'] == 0:
            dd[s+'first_time'] = ptime
        dd[s+'last_time'] = ptime
        d[s+'variance_time'] += ptime**2
        dd[s+'avg_time'] += ptime
        d[s+'sum_len'] += plen
        d[s+'variance_len'] += plen**2
        d[s+'avg_len'] += plen
        if d[s+'first_len'] == 0:
            d[s+'first_len'] = plen
        if ip1 == src:
            dd[s+'out'] += 1
            dd[s+'out_len'] += plen
        elif ip2 == src:
            dd[s+'in'] += 1
            dd[s+'in_len'] += plen

    for _, (d, dd) in flows.items():
        for k, v in dd.items():
            p, q = k.split('#')
            if q == 'first_time':
                d[p+'#duration'] -= v
            elif q == 'last_time':
                d[p+'#duration'] += v
            elif q == 'in':
                d[p+'#sym_corr'] -= math.log(1+v)
            elif q == 'out':
                d[p+'#sym_corr'] += math.log(1+v)
            elif q == 'in_len':
                d[p+'#sym_len_corr'] -= math.log(1+v)
            elif q == 'out_len':
                d[p+'#sym_len_corr'] += math.log(1+v)
            elif q == 'avg_time':
                dd[k] = v/d[p+'#num_pkts']
        for k, v in d.items():
            p, q = k.split('#')
            if q == 'avg_len':
                d[k] = v/d[p+'#num_pkts']
            elif q.endswith('corr'):
                d[k] = abs(v)

    for _, (d, dd) in flows.items():
        for k, v in d.items():
            p, q = k.split('#')
            if q == 'variance_time':
                d[k] = v/d[p+'#num_pkts'] - dd[p+'#avg_time']**2
            elif q == 'variance_len':
                d[k] = v/d[p+'#num_pkts'] - d[p+'#avg_len']**2

    feature_dicts = []
    flow_ids = []
    for k, (d, dd) in flows.items():
        feature_dicts.append(d)
        flow_ids.append(k)

    return feature_dicts, flow_ids

def get_feature_dict(pcap_path, pickle_root=None, ignore_protocols=False):
    if pickle_root is not None:
        pf = pcap_path.replace('/', '_').replace('\\', '_').replace('.', '_')
        if ignore_protocols:
            pf += '_csv'
        pf += '.pickle'
        pickle_path = os.path.join(pickle_root, pf)
        if os.path.isfile(pickle_path):
            print('loaded from', pickle_path)
            return pickle.load(open(pickle_path, 'rb'))
        else:
            print('fresh feature extraction...', end='\r')
            start = time.time()
            D, F = calc_feature_dict(pcap_path, ignore_protocols)
            finish = time.time()
            print('feature extraction time:', finish-start, 's')
            pickle.dump((D, F), open(pickle_path, 'wb'))
            return D, F
    else:
        return calc_feature_dict(pcap_path, ignore_protocols)
