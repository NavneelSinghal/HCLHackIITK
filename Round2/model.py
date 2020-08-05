from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction import DictVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import *
import time
import os
import pickle
import collections
import math

def prune_features(D):
    for d in D:
        dl = []
        ad = collections.defaultdict(int)
        for k, v in d.items():
            h, t = k.split('#')
            npr = 1/d[h+'#num_pkts']
            nlr = d[h+'#avg_len']/d[h+'#sum_len']
            if t == 'in_ratio':
                if v < 0.5:
                    ad[h+'#sym_corr'] -= math.log(npr+v)
                else:
                    ad[h+'#sym_corr'] += math.log(npr+v)
                dl.append(k)
            elif t == 'out_ratio':
                if v <= 0.5:
                    ad[h+'#sym_corr'] -= math.log(npr+v)
                else:
                    ad[h+'#sym_corr'] += math.log(npr+v)
                dl.append(k)
            elif t == 'in_len_ratio':
                if v < 0.5:
                    ad[h+'#sym_len_corr'] -= math.log(nlr+v)
                else:
                    ad[h+'#sym_len_corr'] += math.log(nlr+v)
                dl.append(k)
            elif t == 'out_len_ratio':
                if v <= 0.5:
                    ad[h+'#sym_len_corr'] -= math.log(nlr+v)
                else:
                    ad[h+'#sym_len_corr'] += math.log(nlr+v)
                dl.append(k)
            elif t == 'first_time':
                ad[h+'#duration'] -= v
                dl.append(k)
            elif t == 'last_time':
                ad[h+'#duration'] += v
                dl.append(k)
            elif t == 'min_len' or t == 'max_len' or t == 'last_len':
                dl.append(k)
            elif t == 'avg_time' or t == 'variance_time':
                dl.append(k)
        for k in dl:
            d.pop(k)
        for k, v in ad.items():
            d[k] = v
    return D

def calc_trained_classifier(D, y):
    D = prune_features(D)
    pipe = make_pipeline(
        DictVectorizer(),
        GradientBoostingClassifier()
        #RandomForestClassifier()
        #DecisionTreeClassifier()
    )
    print('training...', end='\r')
    start = time.time()
    pipe.fit(D, y)
    finish = time.time()
    print('training time:', finish-start, 's')
    print('training time per traffic:', (finish-start)/len(y), 's')
    return pipe

def load_trained_classifier(pickle_root):
    pickle_path = os.path.join(pickle_root, 'model.pickle')
    if os.path.isfile(pickle_path):
        return pickle.load(open(pickle_path, 'rb'))
    else:
        return None

def get_trained_classifier(D, y, pickle_root=None):
    clf = calc_trained_classifier(D, y)
    if pickle_root is not None:
        pickle_path = os.path.join(pickle_root, 'model.pickle')
        pickle.dump(clf, open(pickle_path, 'wb'))
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
