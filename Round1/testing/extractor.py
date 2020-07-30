import json

'''
Info

Duration 	    Integer

Network

UDP_requests 	    Integer
IRC_requests 	    Integer
http_requests 	    Integer
smtp_requests 	    Integer
tcp_requests 	    Integer
hosts_contacted     Integer
DNS_requests 	    Integer
domains_contacted   Integer
ICMP_requests 	    Integer

Usage

CPU_usage 	Integer
mem_usage 	Integer

Dropped

Dropped 	Integer

API categories

Noti_API 	Integer
Certi_API 	Integer
Crypto_API 	Integer
exception_API 	Integer
file_API 	Integer
iexplore_API 	Integer
misc_API 	Integer
netapi_API 	Integer
network_API 	Integer
ole_API 	Integer
process_API 	Integer
registry_API 	Integer
resource_API 	Integer
services_API 	Integer
Syn_API 	Integer
system_API 	Integer
ui_API 	        Integer
other_API 	Integer

API summaries

files_accessed 	Integer
files_written 	Integer
files_deleted 	Integer
Mutexes 	Integer
executed_cmds 	Integer
started_servicesInteger
files_read 	Integer
resolved_APIs 	Integer
created_servicesInteger

Processes

processes_generated 	Integer

API name and its frequency

API (321) 	Integer

Malware Family

Family 	Categorical
'''


def extract(path):
    x = json.load(open(path, 'rb'))
    print(x['info']['duration'])
    print(len(x['network']['udp']))
    #print(x)

extract('a2adb204386fab44cf0b79d12bf68f1e64787a60e5b730e118ee71865697851a.json')
