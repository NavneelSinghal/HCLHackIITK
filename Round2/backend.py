import sys
import os
import subprocess
import glob
import collections
import pickle

def get_dns_ips(pcap_path):
    #lines = os.popen("tshark -r \'" + pcap_path + "\' -Y 'dns && dns.flags.response == 1' -T fields -e dns.a").readlines();
    proc = subprocess.Popen(
        ['tshark', '-r', pcap_path, '-Y', 'dns && dns.flags.response == 1', '-T', 'fields', '-e', 'dns.a'],
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        universal_newlines = True
    )
    outs, errs = proc.communicate()
    lines = [l for l in outs.split('\n') if l.rstrip()]
    ret = []
    for l in lines:
        ret += l.split(',')
    return ret

def calc_feature_dict(pcap_path):
    dns_ips = set(get_dns_ips(pcap_path))
    pipe = os.popen('tshark -r '+pcap_path)
    flows = collections.defaultdict(lambda: collections.defaultdict(float))

    while True:
        try:
            line = pipe.readline()
        except:
            break
        if not line:
            break
        try:
            l = line.split(' ')
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
            #print(f'Failed at ({proto}): {line}')
            continue
        ip1, ip2 = sorted([src, dest])
        d = flows[ip1, ip2]
        s = proto+'#'
        d[s+'num_pkts'] += 1
        if d[s+'first_time'] == 0:
            d[s+'first_time'] = ptime
        d[s+'last_time'] = ptime
        d[s+'variance_time'] += ptime**2
        d[s+'avg_time'] += ptime
        if d[s+'min_len'] == 0:
            d[s+'min_len'] = plen
        else:
            d[s+'min_len'] = min(d[s+'min_len'], plen)
        d[s+'max_len'] = max(d[s+'max_len'], plen)
        d[s+'sum_len'] += plen
        d[s+'variance_len'] += plen**2
        d[s+'avg_len'] += plen
        if d[s+'first_len'] == 0:
            d[s+'first_len'] = plen
        d[s+'last_len'] = plen
        if ip1 == src:
            d[s+'out_ratio'] += 1
            d[s+'out_len_ratio'] += plen
        elif ip2 == src:
            d[s+'in_ratio'] += 1
            d[s+'in_len_ratio'] += plen

    for _, d in flows.items():
        for k, v in d.items():
            p, q = k.split('#')
            if q == 'avg_time' or q == 'avg_len' or q == 'out_ratio' or q == 'in_ratio':
                d[k] = v/d[p+'#num_pkts']
            elif q == 'out_len_ratio' or q == 'in_len_ratio':
                d[k] = v/d[p+'#sum_len']

    for _, d in flows.items():
        for k, v in d.items():
            p, q = k.split('#')
            if q == 'variance_time':
                d[k] = v/d[p+'#num_pkts'] - d[p+'#avg_time']**2
            elif q == 'variance_len':
                d[k] = v/d[p+'#num_pkts'] - d[p+'#avg_len']**2

    feature_dicts = []
    flow_ids = []
    for k, v in flows.items():
        feature_dicts.append(v)
        flow_ids.append(k)

    return feature_dicts, flow_ids

def pickle_name(path):
    return path.replace('/', '_').replace('\\', '_').replace('.', '_')+'.pickle'

def get_feature_dict(pcap_path, pickle_root=None):
    if pickle_root is not None:
        pf = pickle_name(pcap_path)
        pickle_path = os.path.join(pickle_root, pf)
        if os.path.isfile(pickle_path):
            return pickle.load(open(pickle_path, 'rb'))
        else:
            D, F = calc_feature_dict(pcap_path)
            pickle.dump((D, F), open(pickle_path, 'wb'))
            return D, F
    else:
        return calc_feature_dict(pcap_path)
