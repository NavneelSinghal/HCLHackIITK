import json

def get_feature_vector(jsonfile):
    with open(jsonfile, 'r') as f:
        data = json.load(f)
    feature = []

    # Parse info section
    info = data.get('info', None)
    if info == None:
        print('Info section missing, possibly corrupted')
        duration = 0
    else:
        duration = int(info.get('duration', 0))
    feature.append(duration)

    # Parse signatures
    signatures = data.get('signatures', None)
    if signatures == None:
        print('Signatures missing, possibly corrupted')
        max_severity = 0
    else:
        max_severity = 0
        for sig in signatures:
            max_severity = max(max_severity, sig.get('severity', 0))
    feature.append(max_severity)

    # Parse network section
    network = data.get('network', None)
    stats = {
            'udp': 0,
            'http': 0,
            'irc': 0,
            'tcp': 0,
            'smtp': 0,
            'hosts': 0,
            'dns': 0,
            'domains': 0,
            'icmp': 0
            }
    if network == None:
        print('Network missing, possibly corrupted')
    else:
        for stat, vals in network.items():
            if stat in stats:
                stats[stat] = len(vals)
    feature.extend(stats.values())

    # Parse behavior section
    behavior = data.get('behavior', None)
    cnt_process = 0
    api_categories = {
            'noti': 0,
            'certi': 0,
            'crypto': 0,
            'exception': 0,
            'file': 0,
            'iexplore': 0,
            'misc': 0,
            'netapi': 0,
            'network': 0,
            'ole': 0,
            'process': 0,
            'registry': 0,
            'resource': 0,
            'services': 0,
            'syn': 0,
            'system': 0,
            'ui': 0,
            'other': 0
            }
    # api_calls = {
    #         'NtOpenFile': 0,
    #         'NtCreateFile': 0,
    #         'CopyFileA': 0,
    #         'DeleteFileA': 0,
    #         'StartServiceA': 0,
    #         'RegSetValueExA': 0,
    #         'RegCreateKeyExA': 0,
    #         'RegDeleteKeyA': 0,
    #         }
    if behavior == None:
        print('Behaviour not found. Possibly corrupted')
        apis = {}
    else:
        processes = behavior['processes']
        cnt_process = len(processes)
        apis = {}
        for process in processes:
            calls = process['calls']
            for call in calls:
                if call['category'] in api_categories:
                    api_categories[call['category']] += 1
                if call['api'] in apis:
                    apis[call['api']] += 1
                else:
                    apis[call['api']] = 1

    feature.append(cnt_process)
    feature.extend(api_categories.values())

    return feature, apis
