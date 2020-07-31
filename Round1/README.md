# Malware Detection using Ensemble Learning

In this round, we implemented malware detection using ensemble learning.

## Installation Instructions

## Running Instructions


usage: 
```
python3 MLDetect.py [-h] [--train] [--validate] [--predict] [--split SPLIT] [--model [{all,string,structure,dynamic}]] [--output [OUTPUT]] [--choose [n]] [inputs [inputs ...]]

Detect malware using machine learning

positional arguments:
  inputs                Directories to search for input files

optional arguments:
  -h, --help            show this help message and exit
  --train               Use the input data to train the model
  --validate            Use the input data to validate the model
  --predict             Predict output on the input data
  --split SPLIT         (only for train) train-test ratio to use
  --model [{all,string,structure,dynamic}]
                        which models to use
  --output [OUTPUT]     (only for predict) save the output to a file, use stdout to print
  --choose [n]          Use only n randomly sampled files from the input
```

## Model Description

We had access to three kinds of data from any given binary: 

1. String dump from the file which contains readable characters

2. Structure information from the PE file

3. Dynamic malware analysis data from the Cuckoo Sandbox.

We considered three separate models for each type of data, and then used a consensus based classification for all data which had all three results available, while using the best accuracy available model for each of the remaining binaries (in case not all three types of data are available for a binary). This was done even though the accuracy was quite high on each model so as to ensure high confidence in the results (as well as reduction of error). 

For each of the three models, we used feature hashing (due to occasionally missing data and also to reduce the dimensionality of data), random forest classification (which is in itself ensemble learning) and parameter tuning.
We also used multiclass classification and lumped the malware categories into one class after prediction, instead of using a binary classifier. This was done because it was observed that within malware classes, the features are highly correlated, while across malware classes, this was not observed to be the case (a possible justification is that similarly behaving malwares are in the same class, and they often have a very similar skeleton of code).

// this was verified by rishabh and me

### String analysis

#### Feature Extraction

Our features here were the frequencies of strings corresponding to the binary, which had no special characters other than an underscore, and which were of length at least 5. This was in alignment with our first observations in result analysis.

### Structure analysis

For analysis of the PE files, we wrote a parser to parse information, and used some things as features.
TODO:
mention parser and the basic ideas behind the model and feature selection

### Dynamic analysis

For analysis of this file, we chose the following features:

1. Duration.

2. Severity mentioned in the signature

2. Frequency of the following types of requests: udp, http, irc, tcp, smtp, dns, icmp

3. The number of domains and hosts contacted

4. Frequency of the following types of API categories: noti, certi, crypto, exception, file, iexplore, misc, netapi, network, ole, process, registry, resource, services, syn, system, ui, other

5. Frequencies of any kinds of API calls

To extract these features, we used a simple parser for json files.

## Result Analysis

1. filtered uot artefacts - then filtered out manually

2. Strings relative frequency of keywords - like dll names

3. benign - overall number of keyywords more

4. feature hashing for this

5. dynamic - signatures had cuckoo sandbox - so read stuff - signatures header - severity and all (max severity is a feature). then studied the different kinds of api calls like old approach (using paper)

6. structure analysis - ask rishabh about it 

## Appendix
```
python3 MLDetect.py --train .
{'train': True, 'validate': False, 'predict': False, 'split': 0.75, 'model': 'all', 'output': 'output.csv', 'choose': 0, 'inputs': ['.']}
Total 10002 String.txt(s) detected.
Total 10003 Structure_Info.txt(s) detected.
Total 9958 JSON(s) detected.
Loading all 3 models ...
Training on 9955 hashes 3 models seperately ...
Starting feature extraction
Completed extracting features from 7466 files
Feature extraction completed in 154.9520823955536 seconds
Starting training model
Training completed in 19.345020294189453 seconds
Starting feature extraction
Completed extracting features from 2489 files
Feature extraction completed in 58.831676721572876 seconds
Starting testing
Testing completed in 2.5526962280273438 seconds
accuracy:			 0.9803133788670149
f1 score (micro):		 0.9803133788670149
precision score (micro):	 0.9803133788670149
recall score (micro):		 0.9803133788670149
f1 score (macro):		 0.9803026830671812
precision score (macro):	 0.9801835785481885
recall score (macro):		 0.9805615878801981
Starting feature extraction
Completed extracting features from 7464 files
Feature extraction completed in 122.7312753200531 seconds
Starting training model
Training completed in 10.537144184112549 seconds
Starting feature extraction
Completed extracting features from 2488 files
Feature extraction completed in 44.54435968399048 seconds
Starting testing
Testing completed in 0.8261034488677979 seconds
accuracy:			 0.976295701084773
f1 score (micro):		 0.976295701084773
precision score (micro):	 0.976295701084773
recall score (micro):		 0.976295701084773
f1 score (macro):		 0.9762711875361646
precision score (macro):	 0.976213572155148
recall score (macro):		 0.9763367063699843
Starting feature extraction
Corrupted json, reverting to library defaults
Completed extracting features from 7464 files
Feature extraction completed in 481.3193688392639 seconds
Starting training model
Training completed in 8.205965995788574 seconds
Starting feature extraction
Completed extracting features from 2489 files
Feature extraction completed in 157.39156913757324 seconds
Starting testing
Testing completed in 0.8316993713378906 seconds
accuracy:			 1.0
f1 score (micro):		 1.0
precision score (micro):	 1.0
recall score (micro):		 1.0
f1 score (macro):		 1.0
precision score (macro):	 1.0
recall score (macro):		 1.0

 Now checking ensembled validity ...
Starting feature extraction
Completed extracting features from 2489 files
Feature extraction completed in 53.15453386306763 seconds
Starting testing
Testing completed in 2.476295232772827 seconds
Starting feature extraction
Completed extracting features from 2488 files
Feature extraction completed in 43.526689291000366 seconds
Starting testing
Testing completed in 0.8072757720947266 seconds
Starting feature extraction
Corrupted json, reverting to library defaults
Completed extracting features from 2489 files
Feature extraction completed in 149.8770833015442 seconds
Starting testing
Testing completed in 0.3803224563598633 seconds
accuracy:			 1.0
f1 score (micro):		 1.0
precision score (micro):	 1.0
recall score (micro):		 1.0
f1 score (macro):		 1.0
precision score (macro):	 1.0
recall score (macro):		 1.0
```
