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

# names of files where we'll store data when we extract it

predict_filename = 'temp_dynprediction_dump.sav'
feature_list_filename = 'temp_dynfeature_dump.sav'
feature_dict_filename = 'temp_dyndict_dump.sav'
test_predict_filename = 'temp_dyntest_prediction_dump.sav'
test_feature_list_filename = 'temp_dyntest_feature_list_filename_dump.sav'
test_dict_filename = 'temp_dyntest_dict_dump.sav'

# function to extract features from training and test data

def extract_features():

    start_time = time()

    # fraction of elements which are going to be used for training
    train_fraction = 0.75

    # shuffled list of all target directory names to ensure sufficient randomization in train and test set
    total = utility.get_all('Dynamic_Analysis_Data_Part1') + utility.get_all('Dynamic_Analysis_Data_Part2')
    random.shuffle(total)

    # training and test target directories
    train = total[:int(train_fraction * len(total))]
    test = total[len(train):]

    # storage for predictions and feature lists (one part is a dictionary which works with APIs)
    predictions = []
    feature_list = []
    feature_dict = []

    print("now working on train")

    complete = 0

    # processing each directory in the training set
    for fl in train:
        w = -1
        for i in range(len(classes)):
            if fl.count(classes[i]) > 0:
                w = i
                break
        # w is now the actual class of the directory
        assert(w != -1)
        predictions.append(w)

        # feature list and feature dictionary being extracted (feature dictionary will be hashed later on)
        feat_list, dictionary = dynamic_analysis.get_feature_vector(fl)
        feature_list.append(feat_list)
        feature_dict.append(dictionary)
        complete += 1

        # to estimate speed
        if complete % 50 == 0:
            print (str(complete) + " done")

    # storage for predictions and feature lists and dictionaries for test data
    test_predictions = []
    test_feature_list = []
    test_feature_dict = []

    print("now working on test")

    complete = 0

    # processing each directory in the test set
    for fl in test:
        w = -1
        for i in range(len(classes)):
            if fl.count(classes[i]) > 0:
                w = i
                break
        # w is now the actual class of the directory
        assert(w != -1)
        test_predictions.append(w)

        # feature list and feature dictionary being extracted (feature dictionary will be hashed later on)
        feat_list, dictionary = dynamic_analysis.get_feature_vector(fl)
        test_feature_list.append(feat_list)
        test_feature_dict.append(dictionary)
        complete += 1

        # to estimate speed
        if complete % 50 == 0:
            print (str(complete) + " done")

    # storing the data for the training set offline
    pickle.dump(predictions, open(predict_filename, 'wb'))
    pickle.dump(feature_list, open(feature_list_filename, 'wb'))
    pickle.dump(feature_dict, open(feature_dict_filename, 'wb'))

    # storing the data for the test set offline
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
    # hasher for the dictionaries where we do not know the number of features
    h = FeatureHasher(n_features = feat)

    # hash of the list of the feature dictionaries of the each training directory
    X = h.transform(pickle.load(open(feature_dict_filename, 'rb'))).toarray()

    # appending the vector corresponding to the already found list of features for each file in the training directory
    X = np.concatenate((X, np.array(pickle.load(open(feature_list_filename, 'rb')))), axis = 1)

    # loading the categories for the training sets
    y = np.array(pickle.load(open(predict_filename, 'rb')))

    # we use a random forest classifier to achieve better results using ensemble learning
    clf = RandomForestClassifier()

    # fit the classifier to the training data
    clf.fit(X, y)

    # store the model into a file
    pickle.dump(clf, open('modeldyn_parameters.sav', 'wb'))

    end_time = time()

    print ('Training complete in ' + str(end_time - start_time) + ' seconds')

def test():

    from sklearn.feature_extraction import FeatureHasher
    from sklearn.ensemble import RandomForestClassifier
    from sklearn import metrics

    feat = 7000
    # hasher for the dictionaries where we do not know the number of features
    h = FeatureHasher(n_features = feat)

    start_time = time()

    # hash of the list of the feature dictionaries of the each test directory
    TX = h.transform(pickle.load(open(test_dict_filename, 'rb'))).toarray()

    # appending the vector corresponding to the already found list of features for each file in the test directory
    TX = np.concatenate((TX, np.array(pickle.load(open(test_feature_list_filename, 'rb')))), axis = 1)

    # loading the categories for the test sets
    Ty = np.array(pickle.load(open(test_predict_filename, 'rb')))

    # load the saved model
    clf = pickle.load(open('modeldyn_parameters.sav', 'rb'))

    # predict the values for test data
    prediction_values = clf.predict(TX)

    # function to see if a class corresponds to benign binaries or malware
    f = lambda x: 1 if x > 0 else 0

    def fromiter(x):
        return np.fromiter((f(xi) for xi in x), x.dtype)

    # lump all malware predictions/categories into one
    prediction_values = fromiter(prediction_values)
    Ty = fromiter(Ty)

    # print statistics from the data
    print("features:", feat)
    print("accuracy:", metrics.accuracy_score(prediction_values, Ty))
    print("f1 score:", metrics.f1_score(prediction_values, Ty, average = 'micro'))
    print("precision score:", metrics.precision_score(prediction_values, Ty, average = 'micro'))
    print("recall score:", metrics.recall_score(prediction_values, Ty, average = 'micro'))
    print("f1 score (macro):", metrics.f1_score(prediction_values, Ty, average = 'macro'))
    print("precision score (macro):", metrics.precision_score(prediction_values, Ty, average = 'macro'))
    print("recall score (macro):", metrics.recall_score(prediction_values, Ty, average = 'macro'))

    # finding the number of wrong predictions
    mismatch = 0
    tot = prediction_values.shape[0]
    for i in range(tot):
        mismatch += 1 if prediction_values[i] != Ty[i] else 0

    print("mismatches:", mismatch)

    # printing the whole prediction array
    print("prediction is", prediction_values.tolist())

    # printing the whole category array
    print("y is", Ty.tolist())

    end_time = time()

    print ('Testing complete in ' + str(end_time - start_time) + ' seconds')

#extract_features()
train()
test()
