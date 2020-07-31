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

def labelled(x):
    if x[2] == None:
        return False
    return True

def all(other=lambda x: True):
    def decision(leaf):
        return other(leaf)
    return decision

def benigns(other=lambda x: True):
    def decision(leaf):
        if not 'benign' in str(leaf.parent).lower():
            return False
        return other(leaf)
    return decision

def malwares(other=lambda x: True):
    def decision(leaf):
        if not 'malware' in str(leaf.parent).lower():
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
    files = []
    def scan(start, label=None):
        if start.is_file():
            if filt(start):
                if start.suffix == '.txt':
                    hash = start.parent.name
                elif start.suffix == '.json':
                    hash = start.stem
                else:
                    return
                files.append((hash, str(start), label))
        else:
            for f in start.iterdir():
                if f.name.lower() in labels:
                    label = labels[f.name.lower()]
                scan(f, label)

    root = Path(root)
    if not root.exists():
        print('Check root directory path if it even exists')
        return
    scan(root)
    return files
