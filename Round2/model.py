from sklearn.ensemble import GradientBoostingClassifier
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import *
import time
import os
import pickle
import collections

def output_csv(D, y, csv_path):
    fl = open(csv_path, 'w')
    fcols = {}
    head = ''
    for d in D:
        for k in d.keys():
            if k not in fcols:
                fcols[k] = len(fcols)
                head += k+','
    print(head[:-1], file=fl)
    mat = [[0. for _ in range(len(fcols))] for _ in range(len(D))]
    for i in range(len(D)):
        d = D[i]
        for k, v in d.items():
            mat[i][fcols[k]] = v
    for i in range(len(mat)):
        for val in mat[i]:
            print(val, end=',', file=fl)
        print(int(y[i]), file=fl)

def load_D_y_from_csv(csv_path):
    lines = open(csv_path, 'r').readlines()
    lines = [l.rstrip() for l in lines]

    heads = lines[0].split(',')
    inv = []
    for h in heads:
        inv.append(h)

    D = []
    y = []
    for l in lines[1:]:
        d = {}
        vals = l.split(',')
        for i in range(len(vals)-1):
            if vals[i] != 0:
                d[inv[i]] = float(vals[i])
        D.append(d)
        y.append(float(vals[-1]))

    return D, y


def calc_trained_classifier(D, y):
    pipe = make_pipeline(
        DictVectorizer(),
        GradientBoostingClassifier()
    )
    print('training...', end='\r')
    start = time.time()
    pipe.fit(D, y)
    finish = time.time()
    print('training time:', finish-start, 's')
    print('training time per traffic:', (finish-start)/len(y), 's')
    return pipe

def load_trained_classifier(pickle_root, csv_model=False):
    if csv_model:
        pickle_path = os.path.join(pickle_root, 'model_csv.pickle')
    else:
        pickle_path = os.path.join(pickle_root, 'model.pickle')
    if os.path.isfile(pickle_path):
        print('loading from', pickle_path, end='\r')
        start = time.time()
        clf = pickle.load(open(pickle_path, 'rb'))
        finish = time.time()
        print('loaded pre-trained model from', pickle_path, 'in:', finish-start, 's')
        return clf
    else:
        return None

def get_trained_classifier(D, y, pickle_root=None, dump_csv=False):
    if dump_csv:
        f = 'preprocessed.csv'
        print('dumping preprocessed data in', f, '...', end='\r')
        start = time.time()
        #output_csv(D, y, os.path.join(pickle_root, 'model.csv'))
        output_csv(D, y, f)
        finish = time.time()
        print('dumped preprocessed data in', f, 'in:', finish-start, 's')
    clf = calc_trained_classifier(D, y)
    if pickle_root is not None:
        if dump_csv:
            pickle_path = os.path.join(pickle_root, 'model_csv.pickle')
        else:
            pickle_path = os.path.join(pickle_root, 'model.pickle')
        print('dumping trained model in', pickle_path, '...', end='\r')
        start = time.time()
        pickle.dump(clf, open(pickle_path, 'wb'))
        finish = time.time()
        print('dumped trained model in', pickle_path, 'in:', finish-start, 's')
    return clf

def predict(clf, D):
    print('predicting...', end='\r')
    start = time.time()
    y_pred = clf.predict(D)
    finish = time.time()
    print('prediction time:', finish-start, 's')
    print('prediction time per traffic:', (finish-start)/len(D), 's')
    return y_pred

def print_metrics(y_true, y_pred):
    fp_ctr = 0
    fn_ctr = 0
    for i in range(len(y_true)):
        if y_true[i] == 1 and y_pred[i] == 0:
            fn_ctr += 1
        elif y_true[i] == 0 and y_pred[i] == 1:
            fp_ctr += 1
    print('false positives:', fp_ctr, '/', len(y_true))
    print('false negatives:', fn_ctr, '/', len(y_true))
    print('total mismatch:', fp_ctr+fn_ctr, '/', len(y_true))
    print('accuracy:', accuracy_score(y_true, y_pred))
    print('f1 (micro):', f1_score(y_true, y_pred, average='micro'))
    print('recall (micro):', recall_score(y_true, y_pred, average='micro'))
    print('precision (micro):', precision_score(y_true, y_pred, average='micro'))
    print('f1 (macro):', f1_score(y_true, y_pred, average='macro'))
    print('recall (macro):', recall_score(y_true, y_pred, average='macro'))
    print('precision (macro):', precision_score(y_true, y_pred, average='macro'))

def test(clf, D, y):
    y_pred = predict(clf, D)
    print_metrics(y, y_pred)
