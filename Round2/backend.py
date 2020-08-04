import os
import collections

def get_dns_ips(pcap_path):
    lines = os.popen("tshark -r \'" + pcap_path + "\' -Y 'dns.flags.response == 1' -T fields -e dns.a").readlines();
    lines = [l.rstrip() for l in lines if l.rstrip()]
    ret = []
    for l in lines:
        ret += l.split(',')
    return ret

def calc_feature_dict(pcap_path):
    dns_ips = set(get_dns_ips(pcap_path))
    lines = os.popen('tshark -r '+pcap_path).readlines();
    flows = collections.defaultdict(lambda: collections.defaultdict(float))

    for l in lines:
        l = l.split(' ')
        l = [x for x in l if x != '']
        ptime = float(l[1])
        src = l[2]
        dest = l[4]
        if src in dns_ips or dest in dns_ips:
            continue
        proto = l[5]
        plen = int(l[6])
        ip1, ip2 = sorted([src, dest])
        d = flows[ip1, ip2]
        s = proto+'#'
        d[s+'num_pkts'] += 1
        if d[s+'first_time'] == 0:
            d[s+'first_time'] = ptime
        d[s+'last_time'] = ptime
        d[s+'avg_time'] += ptime
        if d[s+'min_len'] == 0:
            d[s+'min_len'] = plen
        else:
            d[s+'min_len'] = min(d[s+'min_len'], plen)
        d[s+'max_len'] = max(d[s+'max_len'], plen)
        d[s+'sum_len'] += plen
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
            if q == 'avg_time' or q == 'avg_len' or q == 'out_ratio':
                d[k] = v/d[p+'#num_pkts']
            elif q == 'out_len_ratio' or q == 'in_len_ratio':
                d[k] = v/d[p+'#sum_len']

    feature_dicts = []
    flow_ids = []
    for k, v in flows.items():
        feature_dicts.append(v)
        flow_ids.append(k)

    return feature_dicts, flow_ids

