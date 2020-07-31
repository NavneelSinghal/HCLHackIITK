#!/usr/bin/env python3

# the full machine learning pipeline after feature extraction
#
# author: Rishabh Ranjan
#
# TODO: theoretically correct use of standard scaling

import structure_analysis
import dynamic_analysis

from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction import FeatureHasher
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

from time import time
from pickle import dump, load
from sys import argv

feature_dict_func = structure_analysis.get_feature_dict_no_indent
num_features = 10000
root = 'Static_Analysis_Data'
train_frac = 0.75
use_frac = 1.0 # fraction of files used to train+test
root_cute = 'static'
time_stamp = str(int(time()))

import glob
import numpy
import os

root = '.'
num_features = 5000
dump_label = 'structure'
glob_str = 'Structure_Info.txt'
time_stamp = str(int(time()))
#get_features = lambda path: ([0.], structure_analysis.get_feature_dict(os.path.split(path)[0]))
get_features = dynamic_analysis.get_feature_vector

class_dict = {
    'benign':0,
    'backdoor':1,
    'trojan':2,
    'trojandownloader':3,
    'trojandropper':4,
    'virus':5,
    'worm':6
}

def get_paths(root, glob_str, use_frac = 1., train_frac = .7):
    paths = glob.glob(os.path.join(root, '**', glob_str), recursive=True)
    class_wise = []
    for _ in range(len(class_dict)):
        class_wise.append([])
    for path in paths:
        h, t = os.path.split(path)
        hh, ht = os.path.split(h)
        _, hht = os.path.split(hh)
        if ht in class_dict:
            class_id = class_dict[ht]
        elif hht in class_dict:
            class_id = class_dict[hht]
        else:
            class_id = None
        if class_id is not None: 
            class_wise[class_id].append(path)
    class_wise_train = []
    class_wise_test = []
    for i in range(len(class_dict)):
        num_use = int(use_frac * len(class_wise[i]))
        num_train = int(train_frac * num_use)
        class_wise_train.append(class_wise[i][:num_train])
        class_wise_test.append(class_wise[i][num_train:num_use])
    train_paths = []
    test_paths = []
    for i in range(len(class_dict)):
        for path in class_wise_train[i]:
            train_paths.append((path, i))
        for path in class_wise_test[i]:
            test_paths.append((path, i))
    return train_paths, test_paths

def get_X_y(paths, get_features):
    L = []
    D = []
    y = []
    for path, class_id in paths:
        try:
            l, d = get_features(path)
        except:
            continue
        L.append(l)
        D.append(d)
        y.append(class_id)
    fh = FeatureHasher(n_features=num_features)
    H = fh.transform(D).toarray()
    X = numpy.concatenate((H, L), axis=1)
    return X, y

def extract():
    #train_paths, test_paths = get_paths('.', 'Structure_Info.txt', 1., .7)
    train_paths, test_paths = get_paths('.', '*.json', 1., .7)
    print('extracting features...')
    start = time()
    X_train, y_train = get_X_y(train_paths, get_features)
    X_test, y_test = get_X_y(test_paths, get_features)
    finish = time()
    print('time for extracting features:', finish-start, 's')
    print('time for extracting features per file:', (finish-start)/len(y_train), 's')
    f = '_Xy_' + root_cute + '_' + str(use_frac).split('.')[-1] + '_' + str(train_frac).split('.')[-1] + '_' + time_stamp
    dump((X_train, y_train, X_test, y_test), open(f, 'wb'))
    print('(X_train, y_train, X_test, y_test) dumped in:', f)
    print('---')
    return X_train, y_train, X_test, y_test

def train(X, y):
    print('training classifier...')
    start = time()
    clf = RandomForestClassifier(random_state=0)
    clf.fit(X, y)
    finish = time()
    print('time for training classifier:', finish-start, 's')
    print('time for training classifier per file:', (finish-start)/len(y), 's')
    f = '_clf_' + root_cute + '_' + time_stamp
    dump(clf, open(f, 'wb'))
    print('classifier dumped in:', f)
    print('---')
    return clf

def get_metrics(y_true, y_pred, binary=True):
    if binary:
        y_true = [(6-y)//6 for y in y_true]
        y_pred = [(6-y)//6 for y in y_pred]
    ctr = 0
    for i in range(len(y_true)):
        if y_true[i] != y_pred[i]:
            ctr += 1
    ret = ''
    ret += 'mismatch:' + str(ctr)
    ret += '\n'
    ret += 'accuracy:' + str(accuracy_score(y_true, y_pred))
    ret += '\n'
    ret += 'f1 (micro):' + str(f1_score(y_true, y_pred, average='micro'))
    ret += '\n'
    ret += 'recall (micro):' + str(recall_score(y_true, y_pred, average='micro'))
    ret += '\n'
    ret += 'precision (micro):' + str(precision_score(y_true, y_pred, average='micro'))
    ret += '\n'
    ret += 'f1 (macro):' + str(f1_score(y_true, y_pred, average='macro'))
    ret += '\n'
    ret += 'recall (macro):' + str(recall_score(y_true, y_pred, average='macro'))
    ret += '\n'
    ret += 'precision (macro):' + str(precision_score(y_true, y_pred, average='macro'))
    ret += '\n'
    f = '_metrics_' + root_cute + '_' + time_stamp
    print(ret, file=open(f, 'w'))
    print('metrics logged in:', f)
    print('---')
    print(ret)
    return ret

def test(clf, X, y):
    print('testing...')
    start = time()
    y_pred = clf.predict(X)
    finish = time()
    print('time for testing:', finish-start, 's')
    print('time for testing per file:', (finish-start)/len(y), 's')
    get_metrics(y, y_pred)

def main():
    if len(argv) < 2 or argv[1] == '-':
        D_train, y_train, D_test, y_test = extract()
    else:
        D_train, y_train, D_test, y_test = load(open(argv[1], 'rb'))
    if len(argv) < 3 or argv[2] == '-':
        clf = train(D_train, y_train)
    else:
        clf = load(open(argv[2], 'rb'))
    test(clf, D_test, y_test)

if __name__ == '__main__':
    main()
