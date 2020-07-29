import string_analysis
import utility
from time import time

st = time()
for fl in utility.get_all('static_samples'):
    string_analysis.get_frequency_map(fl)
end = time()
print ('String feature extraction complete in ' + str(end-st) + ' seconds')
