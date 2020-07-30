# import string_analysis
# import utility
# from time import time

# st = time()
# for fl in utility.get_all('static_samples'):
#     string_analysis.get_frequency_map(fl)
# end = time()
# print ('String feature extraction complete in ' + str(end-st) + ' seconds')

#### Dynamic analysis tester

import dynamic_analysis
import utility
from time import time
from tqdm import tqdm

severity = 0
apis = 0
cnt = 0

st = time()
for benign in tqdm(utility.get_benigns('./dynamic_samples')):
    feat, freq_map = dynamic_analysis.get_feature_vector(benign)
    severity += feat[1]
    apis += len(freq_map)
    cnt += 1
en = time()

print(f'Completed in {en-st:.2f} seconds')
print (f'Average severity found to be {severity/cnt:.2f}')
print (f'Average number of API calls found to be {apis/cnt:.1f}. Use this information to choose optimum value for feature hasher')
