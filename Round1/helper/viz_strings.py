import os
from sys import argv
from random import sample
import matplotlib.pyplot as plt
from math import exp

cutoffLength = 5

# Which are the strings we are interested in? Comment uncomment
def is_valid_string(string):
    # return True # Don't filter at all

    # Filter based on length
    if len(string) < cutoffLength:
        return False

    # Filter some strings
    for c in string:
        if c.isalnum() or c == '_':
            continue
        return False
    return True

def get_features(filename):
    useful, artefact = 0, 0
    bow = 0
    with open(filename, 'r') as strings:
        for line in strings:
            line = line.strip()
            if is_valid_string(line):
                useful += 1
                if line == 'GetProcAddress':
                    bow += 1
            else:
                artefact += 1
    bow = 1 - exp(-(bow/useful)/0.01)
    return (useful, bow)

# Sample some files from the dump
def sample_file_names(directory, k):
    subdirs = [f.path for f in os.scandir(directory) if f.is_dir()]
    subdirs = sample(subdirs, k)
    return subdirs

K = 50 # Number of samples

if __name__ == '__main__':
    statics = argv[1]
    fig, (ax1, ax2) = plt.subplots(1,2)
    ax1.set_yscale('log')
    ax2.set_yscale('linear')
    ax2.set_xscale('linear')
    classes = [
            'benign',
            'malware/backdoor',
            'malware/trojan',
            'malware/trojandownloader',
            'malware/trojandropper',
            'malware/virus',
            'malware/worm'
            ]
    for i, cl in enumerate(classes):
        print('Class in progress: ' + cl)
        path = os.path.join(statics, cl)
        files = sample_file_names(path, K)
        pkd_y = []
        proc_y = []
        for fl in files:
            print(fl)
            packedness, bow = get_features(os.path.join(fl, 'String.txt'))
            pkd_y.append(packedness)
            proc_y.append(bow)
        ax1.scatter([i]*len(pkd_y), pkd_y, alpha=0.5, label=cl)
        ax2.scatter([i]*len(proc_y), proc_y, alpha=0.5, label=cl)
    ax1.legend()
    ax2.legend()
    plt.show()
