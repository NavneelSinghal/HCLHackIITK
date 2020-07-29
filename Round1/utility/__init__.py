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
