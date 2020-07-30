import string_analysis
import utility
from time import time
import pickle
import numpy as np
import random

classes = [
        'Benign',
        'Malware/Backdoor',
        'Malware/Trojan',
        'Malware/Trojandownloader',
        'Malware/Trojandropper',
        'Malware/Virus',
        'Malware/Worm'
        ]

start_time = time()
complete = 0

predictions = []
feature_list = []

predict_filename = 'temp_prediction_dump.sav'
feature_list_filename = 'temp_feature_dump.sav'
test_predict_filename = 'temp_test_prediction_dump.sav'
test_feature_list_filename = 'temp_test_feature_list_filename_dump.sav'


# this is for extraction of features

'''

total = (utility.get_all('Static_Analysis_Data'))
print(len(total))
random.shuffle(total)

train_fraction = 0.75

train = total[:int(train_fraction * len(total))]
test = total[len(train):]

print("now working on train")

for fl in train:
    w = -1
    for i in range(len(classes)):
        if fl.count(classes[i]) > 0:
            w = i
            break
    assert(w != -1)
    predictions.append(w)
    feature_list.append(string_analysis.get_frequency_map(fl))
    complete += 1
    if complete % 50 == 0:
        print (str(complete) + " done")
    #if complete == 1000:
        #break

test_predictions = []
test_feature_list = []

print("now working on test")

complete = 0

for fl in test:
    w = -1
    for i in range(len(classes)):
        if fl.count(classes[i]) > 0:
            w = i
            break
    test_predictions.append(i)
    test_feature_list.append(string_analysis.get_frequency_map(fl))
    complete += 1
    if complete % 50 == 0:
        print (str(complete) + " done")
    #if complete == 1000:
        #break

pickle.dump(predictions, open(predict_filename, 'wb'))
pickle.dump(feature_list, open(feature_list_filename, 'wb'))
pickle.dump(test_predictions, open(test_predict_filename, 'wb'))
pickle.dump(test_feature_list, open(test_feature_list_filename, 'wb'))

end_time = time()

print ('String feature extraction complete in ' + str(end_time - start_time) + ' seconds')

#'''

#this is for training and validating the model

#'''

from sklearn.feature_extraction import FeatureHasher
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics

start_time = time()

feat = 7000
h = FeatureHasher(n_features = feat)

X = h.transform(pickle.load(open(feature_list_filename, 'rb'))).toarray()
y = np.array(pickle.load(open(predict_filename, 'rb')))
TX = h.transform(pickle.load(open(test_feature_list_filename, 'rb'))).toarray()
Ty = np.array(pickle.load(open(test_predict_filename, 'rb')))

clf = RandomForestClassifier()
clf.fit(X, y)

prediction_values = clf.predict(TX)

f = lambda x: 1 if x > 0 else 0

def fromiter(x):
    return np.fromiter((f(xi) for xi in x), x.dtype)

prediction_values = fromiter(prediction_values)
Ty = fromiter(Ty)

print("features:", feat)
print("accuracy:", metrics.accuracy_score(prediction_values, Ty))
print("f1 score:", metrics.f1_score(prediction_values, Ty, average = 'micro'))
print("precision score:", metrics.precision_score(prediction_values, Ty, average = 'micro'))
print("recall score:", metrics.recall_score(prediction_values, Ty, average = 'micro'))

print("prediction is", prediction_values.tolist())
print("y is", Ty.tolist())

pickle.dump(clf, open('model_parameters.sav', 'wb'))

#'''

end_time = time()

print ('Testing complete in ' + str(end_time - start_time) + ' seconds')

