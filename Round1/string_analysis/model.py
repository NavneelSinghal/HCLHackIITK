# author: Navneel Singhal
# functionality: extraction, training and validation

from time import time
import os
import pickle

from sklearn.feature_extraction import FeatureHasher
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
import numpy as np

from .extractor import get_frequency_map

# Other imports


class StringModel:

    def __init__(self, model='string_analysis/model/model.sav'):
        '''
        Load model parameters from the specified model file.
        If not found, assume model not trained.
        '''
        self.model_filename = model

        if os.path.exists(model):
            self.model = pickle.load(open(model, 'rb'))
        else:
            self.model = None

    def train(self, files, labels, save=None):
        '''
        Train the model on files whose file paths have been specified as
        a list. Save the trained model parameters in default location, or if
        specified at a custom location.

        Labels need to be multiclass
        '''

        if not save:
            save = self.model_filename

        assert len(files) == len(labels)

        feature_dictionary_list = []

        print('Starting feature extraction')
        start_time = time()
        completed_files = 0

        for _file in files:
            feature_dictionary_list.append(get_frequency_map(_file))
            completed_files += 1
            print('Completed extracting features from ' + str(completed_files) + ' files', end='\r')

        print('')
        end_time = time()
        print('Feature extraction completed in ' + str(end_time - start_time) + ' seconds')

        print('Starting training model')
        start_time = time()

        features = 7000
        hasher = FeatureHasher(n_features=features)
        features_x = hasher.transform(feature_dictionary_list).toarray()
        features_y = np.array(labels)
        clf = RandomForestClassifier()
        clf.fit(features_x, features_y)

        end_time = time()
        print('Training completed in ' + str(end_time - start_time) + ' seconds')

        pickle.dump(clf, open(save, 'wb'))
        if save == self.model_filename:
            self.model = clf

    def validate(self, files, labels):

        '''
        Labels can be either multiclass or binary
        '''

        f = lambda x: 1 if x > 0 else 0

        def transform(x):
            return np.fromiter((f(a) for a in x), x.dtype)

        labels = np.array(labels)
        labels = transform(labels)
        predictions = self.predict(files)

        print("accuracy:\t\t\t",
              metrics.accuracy_score(predictions, labels))
        print("f1 score (micro):\t\t",
              metrics.f1_score(predictions, labels, average='micro'))
        print("precision score (micro):\t",
              metrics.precision_score(predictions, labels, average='micro'))
        print("recall score (micro):\t\t",
              metrics.recall_score(predictions, labels, average='micro'))
        print("f1 score (macro):\t\t",
              metrics.f1_score(predictions, labels, average='macro'))
        print("precision score (macro):\t",
              metrics.precision_score(predictions, labels, average='macro'))
        print("recall score (macro):\t\t",
              metrics.recall_score(predictions, labels, average='macro'))


    def predict(self, files):
        '''
        return a vector of predicted values for the set of files specified.
        Assume convention, 0=Benign, 1=Malware.
        '''
        assert self.model is not None

        # now extract features from file, hash them and use self.model to return predictions

        start_time = time()

        completed_files = 0
        feature_dictionary_list = []
        print('Starting feature extraction')

        for _file in files:
            feature_dictionary_list.append(get_frequency_map(_file))
            completed_files += 1
            print('Completed extracting features from ' + str(completed_files) + ' files', end='\r')

        print('')

        end_time = time()

        print('Feature extraction completed in ' + str(end_time - start_time) + ' seconds')

        print('Starting testing')

        start_time = time()

        features = 7000
        hasher = FeatureHasher(n_features=features)
        features_x = hasher.transform(feature_dictionary_list).toarray()
        y = self.model.predict(features_x)

        end_time = time()

        print('Testing completed in ' + str(end_time - start_time) + ' seconds')

        f = lambda x: 1 if x > 0 else 0

        def transform(x):
            return np.fromiter((f(a) for a in x), x.dtype)

        return transform(y)
