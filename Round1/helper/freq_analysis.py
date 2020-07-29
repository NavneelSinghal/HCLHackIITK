import os
from random import sample

def sample_file_names(directory, k):
    subdirs = [x[0] for x in os.walk(directory)]
    subdirs = sample(subdirs, k)
    return subdirs

s = input()
subdirs = sample_file_names(s, 10)
# now this is a short list of files we need to sample

frequencies = {}

for filename in subdirs:
    with open(filename + "/String.txt", "r") as f:
        for line in f:
            line = line.strip()
            if line in frequencies:
                frequencies[line] += 1
            else:
                frequencies[line] = 1
    f.close()

result = []

for x in frequencies:
    result.append((frequencies[x], x))

result = sorted(result)
result.reverse()
print(result)
