import pickle
from sklearn.preprocessing import *
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction import DictVectorizer
from sklearn.decomposition import PCA
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt
import random

print('loading...')
D, l = pickle.load(open('pickles/all_Dl.pickle', 'rb'))
print('loaded')
tmp = list(zip(D, l))
random.shuffle(tmp)
D, l = zip(*tmp[:1000])
print(len(D))
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(l)
pipe = make_pipeline(
    DictVectorizer(sparse=False),
    PCA(n_components=3)
)
print('fitting...')
pipe.fit(D, y)
print('transforming')
T = pipe.transform(D)
B = [T[i] for i in range(len(T)) if l[i] == 'Benign']
M = [T[i] for i in range(len(T)) if l[i] == 'Botnet']
print(l)
print('scatter')
ax = plt.axes(projection='3d')
ax.scatter3D(*zip(*B))
ax.scatter3D(*zip(*M))
print('show')
plt.show()
print('end')
