# author: Sarthak Agrawal

# Parameters
CUTOFF_LENGTH = 5

# Which are the strings we are interested in? Comment uncomment
def is_valid_string(string):
    # return True # Don't filter at all

    # Filter based on length
    if len(string) < CUTOFF_LENGTH:
        return False

    # Filter some strings
    for character in string:
        if character.isalnum() or character == '_':
            continue
        return False
    return True

def get_frequency_map(filename):
    frequencies = {}
    with open(filename, 'r') as fil:
        for line in fil:
            line = line.strip()
            if not is_valid_string(line):
                continue
            if line in frequencies:
                frequencies[line] += 1
            else:
                frequencies[line] = 1
    return frequencies
