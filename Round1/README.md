# Malware Detection using Ensemble Learning

In this round, we implemented malware detection using ensemble learning.

## Usage

### Libraries used

Please see `requirements.txt` for a list of python libraries used. Install them with:

```
python3 -m pip install -r requirements.txt
```

### Run using pre-trained model

```
python3 MalwareDetection.py <data_directory>
```

### Train fresh model

```
python3 MalwareDetection.py --train <data_directory>
```

*Note:* Training overwrites the pre-trained models. To restore, use:

```
cp dynamic_analysis/model/model.sav.back dynamic_analysis/model/model.sav
cp string_analysis/model/model.sav.back string_analysis/model/model.sav
cp structure_analysis/model/model.sav.back structure_analysis/model/model.sav
```

### General features

`MalwareDetection.py` offers command-line options for choosing functionalities such as training or validation, and options for model used, outputs, etc. Run `python3 MalwareDetection.py --help` for command-line options.

## Model Description

We had access to three kinds of data for a binary: 

1. String dump from the file which contains readable characters in `Strings.txt`

2. Structure information from the PE file in `Structure_Info.txt`

3. Dynamic malware analysis data from the Cuckoo Sandbox in `<file_hash>.json`

We trained three separate models, one for each type of data. Whenever all three types of data are available, we use a consensus based classification using predictions from each of the three models. Otherwise, we revert to using a single model (decided on the basis of confidence in accuracy, from among models corresponding to available data).

Each of these models was trained as a multiclass classifier (classes being 'benign', 'backdoor', 'trojan', 'trojandownloader', 'trojandropper', 'virus', 'worm')

### String analysis

With these observations our first approach was to build a vocabulary of such keywords which may aid in classification and then record frequency of occurence of each keyword present in vocabulary in the `String.txt` file. To extract the final feature vector.

However, the task of selecting such appropriate keywords proved laborious. The alternative was to keep a very large vocabulary with possibly all the keywords that could appear in String.txt file. However the drawback with such an approach was large size of feature vector. Thus, we adopted the feature hashing trick to do the feature reduction. Using a feature hasher it is possible to transform a arbitrary size frequency table into a fixed size feature vector. We experimented with the size of this feature vector to maximize the accuracy while keeping training times optimal. With these feature vector we tried a few different classifiers such as SVM, but our conlusion was that a Random Forest Classifier gave the best results.

### Structure analysis

We recognized that the `Structure_Info.txt` files contain a human readable dump of executables in PE(portable executable) format, which section code summarized into entropy and hashes. Our strategy for feature extraction was:

1. We take all the 'key: value' pairs with numerical values in each section (eg. '[IMAGE_FILE_HEADER]'). We prefix the section name (eg. 'CODE', '.data', '.rsrc', etc) to the 'key' to get the feature name and 'value' is used as the feature value.

2. For feature names which appear multiple times, eg. for entropy in many sections of the same type, we compute the repetition count, mean, min and max as features.

3. We include the section indents in the feature names to capture nesting, especially in resource related sections.

4. We use presence of all flags in the PE as binary valued features.

5. We use the presence of .dll files as features whose values are the counts of the symbols imported from .dll files.

For feature selection, we used a VarianceThreshold transform which removes features showing little variation across training examples.

Finally, we used a DictVectorizer to vectorize the feature dicts and trained a RandomForestClassifier on the resulting feature matrix for the training examples.

### Dynamic analysis

For analysis of the `file_hash.json` file, we chose the following features:

1. Duration.

2. Severity mentioned in the signature.

2. Frequency of the following types of requests: udp, http, irc, tcp, smtp, dns, icmp.

3. The number of domains and hosts contacted.

4. Frequency of the following types of API categories: noti, certi, crypto, exception, file, iexplore, misc, netapi, network, ole, process, registry, resource, services, syn, system, ui, other.

5. Frequencies of any kinds of API calls.

We used FeatureHasher to vectorize ... and explicitly vectorized ...

We used the concatenation of these two feature matrices to get the final feature matrix and trained a RandomForestClassifier on it for the training examples.

## Results from training and testing on given data

```
python3 MalwareDetection.py --train .
```

```
train_test split: 75% : 25%

--- model for Strings.txt ---
files in training set: 7466
files in test set: 2489
feature extraction time for training set: 92.8 s
training time: 11.3 s
feature extraction time for test set: 27.3 s
testing time: 1.2 s
accuracy: 0.9807
f1 score (micro): 0.9807
precision score (micro): 0.9807
recall score (micro): 0.9807
f1 score (macro): 0.9807
precision score (macro): 0.9805
recall score (macro): 0.9811

--- model for Structure_Info.txt ---
files in training set: 7464
files in test set: 2488
feature extraction time for training set: 69.4 s
training time: 16.3 s
feature extraction time for test set: 22.3 s
testing time: 1.7 s
accuracy: 0.9803
f1 score (micro): 0.9803
precision score (micro): 0.9803
recall score (micro): 0.9803
f1 score (macro): 0.9802
precision score (macro): 0.9801
recall score (macro): 0.9805

--- model for <file_hash>.json ---
files in training set: 7464
files in test set: 2489
feature extraction time for training set: 326.3 s
training time: 5.4 s
feature extraction time for test set: 109.2 s
testing time: 0.4 s
accuracy: 0.9987
f1 score (micro): 0.9987
precision score (micro): 0.9987
recall score (micro): 0.9987
f1 score (macro): 0.9987
precision score (macro): 0.9987
recall score (macro): 0.9988

--- testing on ensemble ---
total extraction time for test set: 102.6 s
testing time: 1.2 s
accuracy: 0.9991
f1 score (micro): 0.9991
precision score (micro): 0.9991
recall score (micro): 0.9991
f1 score (macro): 0.9991
precision score (macro): 0.9991
recall score (macro): 0.9992
```

## Observations

See Observations.doc
