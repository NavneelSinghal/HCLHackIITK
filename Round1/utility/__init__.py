import os

classes = [
        'benign',
        'malware/backdoor',
        'malware/trojan',
        'malware/trojandownloader',
        'malware/trojandropper',
        'malware/virus',
        'malware/worm'
        ]

def get_files(directory):
    '''Given directory return files (hash) in it'''

    for f in os.scandir(directory):
        if f.is_dir():
            yield f.path

def get_all(root):
    for cl in classes:
        yield from get_files(os.path.join(root, cl))
def get_benigns(root):
    return get_files(os.path.join(root, classes[0]))
def get_trojans(root):
    return get_files(os.path.join(root, 'malware/trojan'))
def get_trojandownloaders(root):
    return get_files(os.path.join(root, 'malware/trojandownloader'))
def get_trojandroppers(root):
    return get_files(os.path.join(root, 'malware/trojandropper'))
def get_viruses(root):
    return get_files(os.path.join(root, 'malware/virus'))
def get_worms(root):
    return get_files(os.path.join(root, 'malware/worm'))
