import numpy as np
import json
from urllib.request import Request, urlopen

def class_to_grade (cl: int) -> str:
    if cl == 0:
        return 'Poor'
    elif cl ==1:
        return 'Fair'
    elif cl == 2:
        return 'Good'
    else:
        return 'Excellent'

# Parses testing data
def parse_testdata(url, isURL):
    testing = []
    names = []

    raw = None

    if isURL:
        request = Request(url)
        response = urlopen(request)
        raw = json.loads(response.read())

    else:
        raw = json.load(open('testing.json', 'r'))

    for entry in raw:
        name = next(iter(entry.keys()))
        data = next(iter(entry.values()))
        row_tr = []
        for i in range(1, 11):
            row_tr.append(data[f'score{i}'])

        testing.append(np.array(row_tr))
        names.append(name)

    return (names, np.array(testing))

# Parses training data
def parse_traindata(url):

    def get_class(cl):
        cl = cl.lower()
        if cl == 'poor':
            return 0
        elif cl == 'fair':
            return 1
        elif cl == 'good':
            return 2
        else:
            return 3

    def get_onehot(cl):
        cl = cl.lower()
        if cl == 'poor':
            return [0,0,0,1]
        elif cl == 'fair':
            return [0,0,1,0]
        elif cl == 'good':
            return [0,1,0,0]
        else:
            return [1,0,0,0]

    training = []
    simple_prediction = []
    onehot_prediction = []

    request = Request(url)
    response = urlopen(request)
    raw = json.loads(response.read())

    for entry in raw:
        data = next(iter(entry.values()))
        row_tr = []
        for i in range(1, 11):
            row_tr.append(data[f'score{i}'])

        training.append(np.array(row_tr))

        # Simple Encoding
        simple_prediction.append(get_class(data['grade']))
        # One Hot Encoding
        onehot_prediction.append(get_onehot(data['grade']))

    return (np.array(training), np.array(simple_prediction), np.array(onehot_prediction))
