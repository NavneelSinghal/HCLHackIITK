#!/usr/bin/env python3

# the full machine learning pipeline after feature extraction
#
# author: Rishabh Ranjan
#
# TODO: theoretically correct use of standard scaling

from structure_analysis import get_feature_dict
from utility import *

from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import VarianceThreshold
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction import FeatureHasher
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

from time import time
from pickle import dump, load
from sys import argv

feature_dict_func = get_feature_dict
num_features = 20000
root = 'Static_Analysis_Data'
train_frac = 0.75
use_frac = 1.0 # fraction of files used to train+test
root_cute = 'static'
time_stamp = str(int(time()))

def get_filenames_arr(train_frac):
    benigns = get_benigns(root)
    backdoors = get_backdoors(root)
    trojans = get_trojans(root)
    trojandownloaders = get_trojandownloaders(root)
    trojandroppers = get_trojandroppers(root)
    viruses = get_viruses(root)
    worms = get_worms(root)
    num_used_benigns = int(use_frac * len(benigns))
    num_used_backdoors = int(use_frac * len(backdoors))
    num_used_trojans = int(use_frac * len(trojans))
    num_used_trojandownloaders = int(use_frac * len(trojandownloaders))
    num_used_trojandroppers = int(use_frac * len(trojandroppers))
    num_used_viruses = int(use_frac * len(viruses))
    num_used_worms = int(use_frac * len(worms))
    num_train_benigns = int(train_frac * num_used_benigns)
    num_train_backdoors = int(train_frac * num_used_backdoors)
    num_train_trojans = int(train_frac * num_used_trojans)
    num_train_trojandownloaders = int(train_frac * num_used_trojandownloaders)
    num_train_trojandroppers = int(train_frac * num_used_trojandroppers)
    num_train_viruses = int(train_frac * num_used_viruses)
    num_train_worms = int(train_frac * num_used_worms)
    train = [
        benigns[:num_train_benigns],
        backdoors[:num_train_backdoors],
        trojans[:num_train_trojans],
        trojandownloaders[:num_train_trojandownloaders],
        trojandroppers[:num_train_trojandroppers],
        viruses[:num_train_viruses],
        worms[:num_train_worms]
    ]
    test = [
        benigns[num_train_benigns:num_used_benigns],
        backdoors[num_train_backdoors:num_used_backdoors],
        trojans[num_train_trojans:num_used_trojans],
        trojandownloaders[num_train_trojandownloaders:num_used_trojandownloaders],
        trojandroppers[num_train_trojandroppers:num_used_trojandroppers],
        viruses[num_train_viruses:num_used_viruses],
        worms[num_train_worms:num_used_worms]
    ]

    return train, test

def get_D_y_aux(filenames, category):
    D = []
    y = []
    ctr = 0
    for f in filenames:
        print('category:', category, 'file#:', ctr, end='\r')
        try:
            D.append(feature_dict_func(f))
            y.append(category)
            ctr += 1
        except:
            pass
    print()
    return D, y

def get_D_y(filenames_arr):
    D = []
    y = []
    for c in range(len(filenames_arr)):
        tD, ty = get_D_y_aux(filenames_arr[c], c)
        D += tD
        y += ty
    return D, y

def get_trained_classifier(D, y):
    pipe = make_pipeline(
        FeatureHasher(n_features=num_features),
        # StandardScaler(with_mean=False),
        # VarianceThreshold(),
        RandomForestClassifier(random_state=0)
    )
    pipe.fit(D, y)
    return pipe

def get_metrics(y_true, y_pred, binary=True):
    ret = ''
    if binary:
        y_true = [int(y/6) for y in y_true]
        y_pred = [int(y/6) for y in y_pred]
    ctr = 0
    for i in range(len(y_true)):
        if y_true[i] != y_pred[i]:
            ctr += 1
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
    return ret

def extract():
    print('extracting filenames...')
    train_filenames_arr, test_filenames_arr = get_filenames_arr(train_frac)
    #print('train filenames: benigns =', len(train_filenames_arr[0]), '\tmalwares =', len(train_filenames_arr[1]))
    #print('test filenames:  benigns =', len(test_filenames_arr[0]), '\tmalwares =', len(test_filenames_arr[1]))
    print('extracting train features...')
    start = time()
    D_train, y_train = get_D_y(train_filenames_arr)
    finish = time()
    print('time for extracting train features:', finish-start, 's')
    print('time for extracting train features per train file:', (finish-start)/len(y_train), 's')
    print('number of features:', len(D_train[0]))
    print('extracting test features...')
    start = time()
    D_test, y_test = get_D_y(test_filenames_arr)
    finish = time()
    print('time for extracting test features:', finish-start, 's')
    print('time for extracting test features per train file:', (finish-start)/len(y_train), 's')
    f = '_Dy_' + root_cute + '_' + str(use_frac).split('.')[-1] + '_' + str(train_frac).split('.')[-1] + '_' + time_stamp
    dump((D_train, y_train, D_test, y_test), open(f, 'wb'))
    print('(D_train, y_train, D_test, y_test) dumped in:', f)
    print('---')
    return D_train, y_train, D_test, y_test

def train(D_train, y_train):
    print('training classifier...')
    start = time()
    clf = get_trained_classifier(D_train, y_train)
    finish = time()
    print('time for training classifier:', finish-start, 's')
    print('time for training classifier per train file:', (finish-start)/len(y_train), 's')
    f = '_clf_' + root_cute + '_' + time_stamp
    dump(clf, open(f, 'wb'))
    print('classifier dumped in:', f)
    print('---')
    return clf

def test(clf, D_test, y_test):
    print('testing...')
    start = time()
    y_pred = clf.predict(D_test)
    finish = time()
    print('time for testing:', finish-start, 's')
    print('time for testing per test file:', (finish-start)/len(y_test), 's')
    metrics = get_metrics(y_test, y_pred)
    f = '_metrics_' + root_cute + '_' + time_stamp
    print(metrics, file=open(f, 'w'))
    print('metrics logged in:', f)
    print('---')
    print(metrics)
    return metrics

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
