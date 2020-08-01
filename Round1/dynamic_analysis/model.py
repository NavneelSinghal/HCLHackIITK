# author: Navneel Singhal
# functionality: extraction, training and validation

from time import time
import os
import pickle
import numpy as np

from sklearn.feature_extraction import FeatureHasher
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics

from .extractor import get_feature_vector

# Other imports


class DynamicModel:

    def __init__(self, model='dynamic_analysis/model/model.sav'):
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
        feature_vector_list = []

        print('Starting feature extraction')
        start_time = time()
        completed_files = 0
        correct_labels = []
        cur = -1
        for _file in files:
            cur += 1
            try:
                vector, dictionary = get_feature_vector(_file)
                correct_labels.append(labels[cur])
            except:
                continue
            feature_dictionary_list.append(dictionary)
            feature_vector_list.append(vector)
            completed_files += 1
            print('Completed extracting features from ' + str(completed_files) + ' files', end='\r')

        print('')
        end_time = time()
        print('Feature extraction completed in ' + str(end_time - start_time) + ' seconds')

        print('Starting training model')
        start_time = time()

        features = 7000
        hasher = FeatureHasher(n_features=features)
        feature_x = hasher.transform(feature_dictionary_list).toarray()
        feature_x = np.concatenate((feature_x, np.array(feature_vector_list)), axis=1)
        feature_y = np.array(correct_labels)
        clf = RandomForestClassifier()
        clf.fit(feature_x, feature_y)

        end_time = time()
        print('Training completed in ' + str(end_time - start_time) + ' seconds')

        pickle.dump(clf, open(save, 'wb'))
        if save == self.model_filename:
            self.model = clf

    def validate(self, files, labels):

        '''
        Labels can be either multiclass or binary
        '''

        lump = lambda value: 1 if value > 0 else 0

        def transform(array):
            return np.fromiter((lump(element) for element in array), array.dtype)

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
        feature_vector_list = []
        feature_dictionary_list = []
        print('Starting feature extraction')
        prev = None

        for _file in files:
            try:
                vector, dictionary = get_feature_vector(_file)
                prev = vector
            except:
                vector = prev
                dictionary = {}
            feature_dictionary_list.append(dictionary)
            feature_vector_list.append(vector)
            completed_files += 1
            print('Completed extracting features from ' + str(completed_files) + ' files', end='\r')

        print('')

        end_time = time()

        print('Feature extraction completed in ' + str(end_time - start_time) + ' seconds')

        print('Starting testing')

        start_time = time()

        features = 7000
        hasher = FeatureHasher(n_features=features)
        feature_x = hasher.transform(feature_dictionary_list).toarray()
        feature_x = np.concatenate((feature_x, np.array(feature_vector_list)), axis=1)
        feature_y = self.model.predict(feature_x)

        end_time = time()

        print('Testing completed in ' + str(end_time - start_time) + ' seconds')

        lump = lambda value: 1 if value > 0 else 0

        def transform(array):
            return np.fromiter((lump(element) for element in array), array.dtype)

        return transform(feature_y)
