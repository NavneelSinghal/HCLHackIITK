from sklearn.tree import DecisionTreeClassifier
import parser

train_url = 'https://mettl-arq.s3-ap-southeast-1.amazonaws.com/questions/iit-kanpur/cyber-security-hackathon/round1/problem2/xxl0d69v8w/training.json'

test_url = None

def train(train_url):
    X, y, _ = parser.parse_traindata(train_url)
    model = DecisionTreeClassifier()
    model = model.fit(X, y)
    return model

def solve(model, test_url, isURL):
    names, a = parser.parse_testdata(test_url, isURL)
    b = model.predict(a)
    answer = {}
    for i in range(len(names)):
        answer[names[i]] = parser.class_to_grade(b[i])
    return answer

model = train(train_url)

print(solve(model, test_url, False))
