# the full machine learning pipeline after feature extraction
#
# author: Rishabh Ranjan
#
# TODO: theoretically correct use of standard scaling

from structure_analysis import get_feature_dict
from utility import get_benigns, get_malwares

from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import VarianceThreshold
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction import FeatureHasher
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

from time import time

feature_dict_func = get_feature_dict
num_features = 1000
root = 'Static_Analysis_Data'
train_frac = 0.75

def get_filenames_arr(train_frac):
    benigns = get_benigns(root)
    malwares = get_malwares(root)
    num_train_benigns = int(train_frac * len(benigns))
    num_train_malwares = int(train_frac * len(malwares))
    train = [benigns[:num_train_benigns], malwares[:num_train_malwares]]
    test = [benigns[num_train_benigns:], malwares[num_train_malwares:]]
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

def get_trained_estimator(D, y):
    pipe = make_pipeline(
        FeatureHasher(n_features=num_features),
        StandardScaler(with_mean=False),
        # VarianceThreshold(),
        RandomForestClassifier(random_state=0)
    )
    pipe.fit(D, y)
    return pipe

def print_metrics(y_true, y_pred):
    print('accuracy:', accuracy_score(y_true, y_pred))
    print('f1 (micro):', f1_score(y_true, y_pred, average='micro'))
    print('recall (micro):', recall_score(y_true, y_pred, average='micro'))
    print('precision (micro):', precision_score(y_true, y_pred, average='micro'))
    print('f1 (macro):', f1_score(y_true, y_pred, average='macro'))
    print('recall (macro):', recall_score(y_true, y_pred, average='macro'))
    print('precision (macro):', precision_score(y_true, y_pred, average='macro'))

def main():
    print('extracting filenames...')
    train_filenames_arr, test_filenames_arr = get_filenames_arr(train_frac)
    print('train filenames: benigns =', len(train_filenames_arr[0]), '\tmalwares =', len(train_filenames_arr[1]))
    print('test filenames:  benigns =', len(test_filenames_arr[0]), '\tmalwares =', len(test_filenames_arr[1]))
    print('---')
    print('extracting train features...')
    start = time()
    D_train, y_train = get_D_y(train_filenames_arr)
    finish = time()
    print('time for extracting train features:', finish-start, 's')
    print('time for extracting train features per train file:', (finish-start)/len(y_train), 's')
    print('number of features:', len(D_train[0]))
    print('---')
    print('training estimator...')
    start = time()
    clf = get_trained_estimator(D_train, y_train)
    finish = time()
    print('time for training estimator:', finish-start, 's')
    print('time for training estimator per train file:', (finish-start)/len(y_train), 's')
    print('---')
    print('extracting test features...')
    start = time()
    D_test, y_test = get_D_y(test_filenames_arr)
    finish = time()
    print('time for extracting test features:', finish-start, 's')
    print('time for extracting test features per train file:', (finish-start)/len(y_train), 's')
    print('---')
    print('testing...')
    y_pred = clf.predict(D_test)
    print('time for testing:', finish-start, 's')
    print('time for testing per test file:', (finish-start)/len(y_test), 's')
    print('---')
    print_metrics(y_test, y_pred)

if __name__ == '__main__':
    main()
