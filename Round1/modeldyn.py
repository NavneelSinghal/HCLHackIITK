# author: Navneel Singhal
# functionality: extraction, training and validation

import dynamic_analysis
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

predict_filename = 'temp_dynprediction_dump.sav'
feature_list_filename = 'temp_dynfeature_dump.sav'
feature_dict_filename = 'temp_dyndict_dump.sav'
test_predict_filename = 'temp_dyntest_prediction_dump.sav'
test_feature_list_filename = 'temp_dyntest_feature_list_filename_dump.sav'
test_dict_filename = 'temp_dyntest_dict_dump.sav'

def extract_features():

    start_time = time()
    predictions = []
    feature_list = []
    feature_dict = []

    total = utility.get_all('Dynamic_Analysis_Data_Part1') + utility.get_all('Dynamic_Analysis_Data_Part2')
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
        #feature_list.append(
        feat_list, dictionary = dynamic_analysis.get_feature_vector(fl)
        feature_list.append(feat_list)
        feature_dict.append(dictionary)
        complete += 1
        if complete % 50 == 0:
            print (str(complete) + " done")
        if complete == 1000:
            break

    test_predictions = []
    test_feature_list = []
    test_feature_dict = []
    print("now working on test")

    complete = 0

    for fl in test:
        w = -1
        for i in range(len(classes)):
            if fl.count(classes[i]) > 0:
                w = i
                break
        feat_list, dictionary = dynamic_analysis.get_feature_vector(fl)
        test_feature_list.append(feat_list)
        test_feature_dict.append(dictionary)
        test_predictions.append(w)
        complete += 1
        if complete % 50 == 0:
            print (str(complete) + " done")
        if complete == 1000:
            break

    pickle.dump(predictions, open(predict_filename, 'wb'))
    pickle.dump(feature_list, open(feature_list_filename, 'wb'))
    pickle.dump(feature_dict, open(feature_dict_filename, 'wb'))

    pickle.dump(test_predictions, open(test_predict_filename, 'wb'))
    pickle.dump(test_feature_list, open(test_feature_list_filename, 'wb'))
    pickle.dump(test_feature_dict, open(test_dict_filename, 'wb'))

    end_time = time()

    print ('String feature extraction complete in ' + str(end_time - start_time) + ' seconds')

def train():

    start_time = time()

    from sklearn.feature_extraction import FeatureHasher
    from sklearn.ensemble import RandomForestClassifier
    from sklearn import metrics

    feat = 7000
    h = FeatureHasher(n_features = feat)

    X = h.transform(pickle.load(open(feature_dict_filename, 'rb'))).toarray()
    X = np.concatenate((X, np.array(pickle.load(open(feature_list_filename, 'rb')))), axis = 1)
    y = np.array(pickle.load(open(predict_filename, 'rb')))

    clf = RandomForestClassifier()
    clf.fit(X, y)
    pickle.dump(clf, open('modeldyn_parameters.sav', 'wb'))

    end_time = time()

    print ('Training complete in ' + str(end_time - start_time) + ' seconds')

def test():

    from sklearn.feature_extraction import FeatureHasher
    from sklearn.ensemble import RandomForestClassifier
    from sklearn import metrics

    feat = 7000
    h = FeatureHasher(n_features = feat)

    start_time = time()

    TX = h.transform(pickle.load(open(test_dict_filename, 'rb'))).toarray()
    TX = np.concatenate((TX, np.array(pickle.load(open(test_feature_list_filename, 'rb')))), axis = 1)
    Ty = np.array(pickle.load(open(test_predict_filename, 'rb')))

    clf = pickle.load(open('modeldyn_parameters.sav', 'rb'))

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

#extract_features()
train()
test()
