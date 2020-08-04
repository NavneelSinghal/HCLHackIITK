from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction import DictVectorizer
from sklearn.preprocessing import LabelEncoder

def get_trained_classifier_and_label_encoder(D, y):
    pipe = make_pipeline(
        DictVectorizer(),
        RandomForestClassifier()
    )
    pipe.fit(D, y)
    return pipe
