# Malware Detection using Ensemble Learning

In this round, we implemented malware detection using ensemble learning.

## Installation Instructions

## Running Instructions

### Quick Instructions

To run tests, run `python3 MalwareDetection.py --predict <path_to_directory>` to get output in a file called output.csv.

To train the model on the data in a directory, run `python3 MalwareDetection.py --train .` (such a run has been shown in the Appendix).

For further details, look at the next section or run `python3 MalwareDetection.py --help`.

### Detailed Documentation

```
python3 MalwareDetection.py [-h] [--train] [--validate] [--predict] [--split SPLIT] [--model [{all,string,structure,dynamic}]] [--output [OUTPUT]] [--choose [n]] [inputs [inputs ...]]

positional arguments:
  inputs                Directories to search for input files

optional arguments:
  -h, --help            Show this help message and exit
  --train               Use the input data to train the model
  --validate            Use the input data to validate the model
  --predict             Predict output on the input data
  --split SPLIT         (only for train) train-to-total data ratio to use
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

We considered three separate models for each type of data, and then used a consensus based classification for all data which had all three results available, while using the best accuracy available model for each of the remaining binaries (in case not all three types of data are available for a binary). This was done even though the accuracy was quite high on each model (roughly 98% on the first two and 99.9-100% on the last model) so as to ensure high confidence and robustness in the results (as well as reduction of error). 

For each of the three models, we used feature hashing (due to occasionally missing data and also to reduce the dimensionality of data), random forest classification (which is in itself ensemble learning) and parameter tuning.
We also used multiclass classification and lumped the malware categories into one class after prediction, instead of using a binary classifier. This was done because it was observed that within malware classes, the features are highly correlated, while across malware classes, this was not observed to be the case (a possible justification is that similarly behaving malwares are in the same class, and they often have a very similar skeleton of code).
This observation was verified by writing a binary classifier as well.

### String analysis

Our features here were the frequencies of strings corresponding to the binary, which had no special characters other than an underscore, and which were of length at least 5. This was in alignment with our first observations in result analysis.

### Structure analysis (TODO: complete)

For analysis of the PE files, we wrote a parser to parse information, and used some things as features.

TODO: In this section, mention only which features were selected. Reasons need to be mentioned in the result analysis sections and not here (do this, no questions asked).

### Dynamic analysis

For analysis of this file, we chose the following features:

1. Duration.

2. Severity mentioned in the signature.

2. Frequency of the following types of requests: udp, http, irc, tcp, smtp, dns, icmp.

3. The number of domains and hosts contacted.

4. Frequency of the following types of API categories: noti, certi, crypto, exception, file, iexplore, misc, netapi, network, ole, process, registry, resource, services, syn, system, ui, other.

5. Frequencies of any kinds of API calls.

To extract these features, we used a simple parser for json files.

## Result Analysis (TODO: complete this and rename this to something more suitable like observations, don't mess around with combining this section with another one - this one is for only observations and why we made those choices, the previous thing was for enlisting our choices for both easy access and understanding)

TODO: complete compilation by copy pasting the result analysis for all three types.

1. filtered uot artefacts - then filtered out manually

2. Strings relative frequency of keywords - like dll names

3. benign - overall number of keyywords more

4. feature hashing for this

5. dynamic - signatures had cuckoo sandbox - so read stuff - signatures header - severity and all (max severity is a feature). then studied the different kinds of api calls like old approach (using paper)

6. structure analysis - ask rishabh about it 

## Appendix
```
python3 MalwareDetection.py --train .
{'train': True, 'validate': False, 'predict': False, 'split': 0.75, 'model': 'all', 'output': 'output.csv', 'choose': 0, 'inputs': ['.']}
Total 10002 String.txt(s) detected.
Total 10003 Structure_Info.txt(s) detected.
Total 9958 JSON(s) detected.
Loading all 3 models ...
Training on 9955 hashes 3 models separately ...
Starting feature extraction
Completed extracting features from 7466 files
Feature extraction completed in 92.87726855278015 seconds
Starting training model
Training completed in 11.322357892990112 seconds
Starting feature extraction
Completed extracting features from 2489 files
Feature extraction completed in 27.37038016319275 seconds
Starting testing
Testing completed in 1.250908374786377 seconds
accuracy:			 0.9807151466452391
f1 score (micro):		 0.9807151466452391
precision score (micro):	 0.9807151466452391
recall score (micro):		 0.9807151466452391
f1 score (macro):		 0.980701985625344
precision score (macro):	 0.9805436187951988
recall score (macro):		 0.981109103864044
Starting feature extraction
Completed extracting features from 7464 files
Feature extraction completed in 69.48432850837708 seconds
Starting training model
Training completed in 16.384986877441406 seconds
Starting feature extraction
Completed extracting features from 2488 files
Feature extraction completed in 22.302918910980225 seconds
Starting testing
Testing completed in 1.7803447246551514 seconds
accuracy:			 0.9803133788670149
f1 score (micro):		 0.9803133788670149
precision score (micro):	 0.9803133788670149
recall score (micro):		 0.9803133788670149
f1 score (macro):		 0.980290931009936
precision score (macro):	 0.9801004571874572
recall score (macro):		 0.9805960437945629
Starting feature extraction
Completed extracting features from 7464 files
Feature extraction completed in 326.3758165836334 seconds
Starting training model
Training completed in 5.45410943031311 seconds
Starting feature extraction
Corrupted json, reverting to library default
Completed extracting features from 2489 files
Feature extraction completed in 109.20313000679016 seconds
Starting testing
Testing completed in 0.4560661315917969 seconds
accuracy:			 0.9987946966653274
f1 score (micro):		 0.9987946966653274
precision score (micro):	 0.9987946966653274
recall score (micro):		 0.9987946966653274
f1 score (macro):		 0.9987946468567112
precision score (macro):	 0.9987883683360259
recall score (macro):		 0.9988038277511961

 Now checking ensembled validity ...
Starting feature extraction
Completed extracting features from 2489 files
Feature extraction completed in 34.609153270721436 seconds
Starting testing
Testing completed in 1.5767693519592285 seconds
Starting feature extraction
Completed extracting features from 2488 files
Feature extraction completed in 23.32192587852478 seconds
Starting testing
Testing completed in 1.2236318588256836 seconds
Starting feature extraction
Completed extracting features from 2489 files
Feature extraction completed in 102.67164993286133 seconds
Starting testing
Testing completed in 0.4361913204193115 seconds
accuracy:			 0.9991964644435516
f1 score (micro):		 0.9991964644435516
precision score (micro):	 0.9991964644435516
recall score (micro):		 0.9991964644435516
f1 score (macro):		 0.999195810070306
precision score (macro):	 0.9991735537190083
recall score (macro):		 0.9992193598750976
```
