import os
from random import sample

# Which are the strings we are interested in? Comment uncomment
def is_valid_string(string):
    # return True # Don't filter at all

    # Filter based on length
    if len(string) < 5:
        return False

    # Filter some strings
    for c in string:
        if c.isalnum() or c == '_':
            continue
        return False
    return True

# Sample some files from the dump
def sample_file_names(directory, k):
    subdirs = [x[0] for x in os.walk(directory)]
    subdirs = sample(subdirs, k)
    return subdirs

s = input()
K = 500 # Number of samples
cutoff = K/16 # Another filtering parameter, set to 0 to disable
subdirs_ = sample_file_names(s, K)
# now this is a short list of files we need to sample

subdirs = []

for subdir in subdirs_:
    if subdir[-1] == '/':
        subdirs.append(subdir[:-1])
    else:
        subdirs.append(subdir)

# The frequency sum array
frequencies = {}

cur = 0

for filename in subdirs:
    with open(filename + "/String.txt", "r") as f:
        for line in f:
            line = line.strip()
            if not is_valid_string(line):
                continue
            if line in frequencies:
                frequencies[line] += 1
            else:
                frequencies[line] = 1
    f.close()

result = []

for keyw in frequencies:
    freq = frequencies[keyw]
    if freq < cutoff:
        continue
    result.append((freq, keyw))

result = sorted(result, reverse=True)
for v, x in result:
    print(str(v) + ": " + str(x))

