import utility
import sklearn
from .extractor import get_frequency_map
# Other imports

class StringModel:

    def __init__ (self, model='string_analysis/model/model.sav'):
        '''
        Load model parameters from the specified model file.
        If not found, assume model not trained.
        '''
        self.model = model
        pass

    def train(self, files, save=None):
        '''
        Train the model on files whose file paths have been specified as
        a list. Save the trained model parameters in default location, or if
        specified at a custom location.
        '''
        if not save:
            save = self.model
        pass

    def predict(self, files):
        '''
        return a vector of predicted values for the set of files specified.
        Assume convention, 0=Benign, 1=Malware.
        '''
        pass
