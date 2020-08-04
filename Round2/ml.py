import pickle
from sklearn.preprocessing import *
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_selection import VarianceThreshold
from sklearn.decomposition import PCA
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt
import random

print('loading...')
D, l = pickle.load(open('all_pickles/all_Dl_474142.pickle', 'rb'))
print('loaded')
tmp = list(zip(D, l))
random.shuffle(tmp)
D, l = zip(*tmp[:10000])
print(len(D))
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(l)
pipe = make_pipeline(
    DictVectorizer(sparse=False),
    VarianceThreshold(),
    StandardScaler(),
    PCA(n_components=2)
)
print('fitting...')
pipe.fit(D, y)
print('transforming')
T = pipe.transform(D)
B = [T[i] for i in range(len(T)) if l[i][:6] == 'Benign']
M = [T[i] for i in range(len(T)) if l[i][:6] == 'Botnet']
print('scatter')
#ax = plt.axes(projection='3d')
#ax.scatter3D(*zip(*B))
#ax.scatter3D(*zip(*M))
ax = plt.axes()
ax.scatter(*zip(*B))
ax.scatter(*zip(*M))
print('show')
plt.show()
print('end')
