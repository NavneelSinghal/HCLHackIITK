from pathlib import Path

labels = {
    'benign':0,
    'backdoor':1,
    'trojan':2,
    'trojandownloader':3,
    'trojandropper':4,
    'virus':5,
    'worm':6
}

def label_as_int(label):
    return labels[label]

def int_as_label(label):
    for k,v in labels.items():
        if v == label:
            return k
    raise ValueError('Incorrect label (should be 0-6)')

def all(other=lambda x: True):
    def decision(leaf):
        return other(leaf)
    return decision

def benigns(other=lambda x: True):
    def decision(leaf):
        if not 'benign' in leaf.lower():
            return False
        return other(leaf)
    return decision

def malwares(other=lambda x: True):
    def decision(leaf):
        if not 'malware' in leaf.lower():
            return False
        return other(leaf)
    return decision

def strings(other=lambda x: True):
    def decision(leaf):
        if not leaf.name.lower() == 'string.txt':
            return False
        return other(leaf)
    return decision

def structures(other=lambda x: True):
    def decision(leaf):
        if not leaf.name.lower() == 'structure_info.txt':
            return False
        return other(leaf)
    return decision

def dynamics(other=lambda x: True):
    def decision(leaf):
        if not leaf.suffix.lower() == '.json':
            return False
        return other(leaf)
    return decision

def get(root, filt):
    def scan(start, label=None):
        if start.is_file():
            if filt(start):
                if start.suffix == '.txt':
                    hash = start.parent.name
                elif start.suffix == '.json':
                    hash = start.stem
                else:
                    return
                yield (hash, str(start), label)
        else:
            for f in start.iterdir():
                if f.name.lower() in labels:
                    label = labels[f.name.lower()]
                yield from scan(f, label)

    root = Path(root)
    if not root.exists():
        print('Check root directory path if it even exists')
        return
    yield from scan(root)
    # for ch in root.iterdir():
    #     if not ch.is_dir():
    #         continue
    #     for ch2 in ch.iterdir():
    #         if not ch2.is_dir():
    #             continue
    #         if ch2.name.lower() == 'benign':
    #             yield from scan(ch2, label_as_int('benign'))
    #         elif ch2.name.lower() == 'malware':
    #             for ch3 in ch2.iterdir():
    #                 if not ch3.is_dir():
    #                     continue
    #                 yield from scan(ch3, label_as_int(ch3.name.lower()))

