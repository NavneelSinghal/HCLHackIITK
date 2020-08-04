from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction import DictVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import *
import time
import os
import pickle

def calc_trained_classifier(D, y):
    pipe = make_pipeline(
        DictVectorizer(),
        RandomForestClassifier()
    )
    print('training...', end='\r')
    start = time.time()
    pipe.fit(D, y)
    finish = time.time()
    print('training time:', finish-start, 's')
    print('training time per traffic:', (finish-start)/len(y), 's')
    return pipe

def get_trained_classifier(D, y, pickle_root=None):
    if pickle_root is not None:
        pickle_path = os.path.join(pickle_root, 'model.pickle')
        if os.path.isfile(pickle_path):
            return pickle.load(open(pickle_path, 'rb'))
        else:
            clf = calc_trained_classifier(D, y)
            pickle.dump(clf, open(pickle_path, 'wb'))
            return clf
    else:
        return calc_trained_classifier(D, y)

def predict(clf, D):
    print('predicting...', end='\r')
    start = time.time()
    y_pred = clf.predict(D)
    end = time.time()
    print('prediction time:', finish-start, 's')
    print('prediction time per traffic:', (finish-start)/len(D), 's')

def print_metrics(y_true, y_pred):
    print('mismatch:', ctr, '/', len(y_true))
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
