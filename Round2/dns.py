from pyshark import FileCapture
import os

def get_dns_resp_ips_pyshark(pcap_path):
    pcap = FileCapture(pcap_path, display_filter='dns.flags.response == 1', only_summaries=True)
    ret = []
    for pkt in pcap:
        try:
            ret.append(pkt.dns.a)
        except:
            continue
    return ret

def get_dns_resp_ips_tshark(pcap_path):
    lines = os.popen("tshark -r \'" + pcap_path + "\' -Y 'dns.flags.response == 1' -T fields -e dns.a").readlines();
    lines = [l.rstrip() for l in lines if l.rstrip()]
    ret = []
    for l in lines:
        ret += l.split(',')
    return ret
