# author: Navneel Singhal
# functionality: extraction, training and validation

import structure_analysis
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

predict_filename = 'struct_temp_prediction_dump.sav'
feature_list_filename = 'struct_temp_feature_dump.sav'
test_predict_filename = 'struct_temp_test_prediction_dump.sav'
test_feature_list_filename = 'struct_temp_test_feature_list_filename_dump.sav'

model_filename = 'model_struct_parameters.sav'

def extract_features():

    start_time = time()
    predictions = []
    feature_list = []

    total = (utility.get_all('Static_Analysis_Data'))
    print(len(total))
    random.shuffle(total)

    train_fraction = 0.75

    train = total[:int(train_fraction * len(total))]
    test = total[len(train):]

    complete = 0
    print("now working on train")
    for fl in train:
        w = -1
        for i in range(len(classes)):
            if fl.count(classes[i]) > 0:
                w = i
                break
        assert(w != -1)
        predictions.append(w)
        feature_list.append(structure_analysis.get_feature_dict(fl))
        complete += 1
        if complete % 50 == 0:
            print (str(complete) + " done")
            #print (fl)

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
        test_predictions.append(w)
        test_feature_list.append(structure_analysis.get_feature_dict(fl))
        complete += 1
        if complete % 50 == 0:
            print (str(complete) + " done")

    pickle.dump(predictions, open(predict_filename, 'wb'))
    pickle.dump(feature_list, open(feature_list_filename, 'wb'))
    pickle.dump(test_predictions, open(test_predict_filename, 'wb'))
    pickle.dump(test_feature_list, open(test_feature_list_filename, 'wb'))

    end_time = time()

    print ('String feature extraction complete in ' + str(end_time - start_time) + ' seconds')

def train():

    start_time = time()

    from sklearn.feature_extraction import FeatureHasher
    from sklearn.ensemble import RandomForestClassifier
    from sklearn import metrics

    feat = 300
    h = FeatureHasher(n_features = feat)

    X = h.transform(pickle.load(open(feature_list_filename, 'rb'))).toarray()
    y = np.array(pickle.load(open(predict_filename, 'rb')))

    clf = RandomForestClassifier()
    clf.fit(X, y)
    pickle.dump(clf, open(model_filename, 'wb'))

    end_time = time()

    print ('Training complete in ' + str(end_time - start_time) + ' seconds')

def test():

    from sklearn.feature_extraction import FeatureHasher
    from sklearn.ensemble import RandomForestClassifier
    from sklearn import metrics

    feat = 7000
    h = FeatureHasher(n_features = feat)

    start_time = time()

    TX = h.transform(pickle.load(open(test_feature_list_filename, 'rb'))).toarray()
    Ty = np.array(pickle.load(open(test_predict_filename, 'rb')))

    clf = pickle.load(open(model_filename, 'rb'))

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
    print("f1 score (macro):", metrics.f1_score(prediction_values, Ty, average = 'macro'))
    print("precision score (macro):", metrics.precision_score(prediction_values, Ty, average = 'macro'))
    print("recall score (macro):", metrics.recall_score(prediction_values, Ty, average = 'macro'))

    print("prediction is", prediction_values.tolist())
    print("y is", Ty.tolist())

    end_time = time()

    print ('Testing complete in ' + str(end_time - start_time) + ' seconds')

extract_features()
#train()
#test()
