# Malware Detection using Ensemble Learning

In this round, we implemented malware detection using ensemble learning.

## Installation Instructions

## Running Instructions

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
