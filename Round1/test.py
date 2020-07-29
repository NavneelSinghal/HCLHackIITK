import string_analysis
import utility
from time import time

st = time()
for fl in utility.get_files('static_samples/benign'):
    string_analysis.get_frequency_map(fl)
end = time()
print ('String feature extraction complete in ' + str(end-st) + ' seconds')
