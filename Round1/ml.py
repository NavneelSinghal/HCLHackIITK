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

feature_dict_func = get_feature_dict
num_features = 1000
root = 'Static_Analysis_Data'

def get_filenames_arr(train_frac):
    malwares = get_malwares(root)
    benigns = get_benigns(root)
    num_train_malwares = int(train_frac * len(malwares))
    num_train_benigns = int(train_frac * len(benigns))
    train = [benigns[:num_train_benigns], malwares[:num_train_malwares]]
    test = [benigns[num_train_benigns:], malwares[num_train_malwares:]]
    return train, test

def get_D_y_aux(filenames, category):
    D = []
    y = []
    for f in filenames:
        try:
            D.append(feature_dict_func(f))
            y.append(category)
        except:
            pass
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
    print("accuracy:", accuracy_score(y_true, y_pred))
    print("f1 (micro):", f1_score(y_true, y_pred, average='micro'))
    print("recall (micro):", recall_score(y_true, y_pred, average='micro'))
    print("precision (micro):", precision_score(y_true, y_pred, average='micro'))
    print("f1 (macro):", f1_score(y_true, y_pred, average='macro'))
    print("recall (macro):", recall_score(y_true, y_pred, average='macro'))
    print("precision (macro):", precision_score(y_true, y_pred, average='macro'))

def main():
    train_filenames_arr, test_filenames_arr = get_filenames_arr(.75)
    D_train, y_train = get_D_y(train_filenames_arr)
    clf = get_trained_estimator(D_train, y_train)
    D_test, y_test = get_D_y(test_filenames_arr)
    y_pred = clf.predict(D_test)
    print_metrics(y_test, y_pred)

if __name__ == '__main__':
    main()
