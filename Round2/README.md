
# P2P Botnet Detection using Machine Learning
In this round, we implemented P2P botnet traffic detection using machine learning techniques.

## Some notes
1. We have used a `tshark` subprocess to parse the pcap files. This gives much greater PCAP parsing speeds than python libraries like `scapy` and `pyshark`. `tshark` is a dependency of `pyshark` anyway, so we decided to use `tshark` raw taking the huge parsing time gains into account.
2. We use the JSON file format (which is a more natural fit than CSV) to dump the pre-processed training data for validation of model as required in the problem specification.
3. We have also included an alternative modelling strategy which can use CSV files for storing and retreiving pre-processed training data. This also gives high performance and accuracy. For using this modelling strategy please use `python3 botnetdetect.py --csv ...` instead of `python3 botnetdetect.py ...`.
6. The tool has been tested on Ubuntu and MacOS. It should work fine on Windows, but we could not test it due to unavailability of a Windows machine and time constraints.

## Installation
1. The tool uses tshark (wireshark's packet dissector) as the parsing engine to read PCAP/PCAPNG files. Therefore you must have tshark installed and available in the PATH environment variable. See https://tshark.dev/setup/install/.
2. Python version 3.6 or greater is required.
3. Scikit-learn is also required, and can be installed as per instructions at https://scikit-learn.org/stable/install.html

## Usage
Full specification:
```
usage: botnetdetect.py [-h] [--train] [--retrain] [--csv]
                       [--validate] [--predict] [--dump]
                       [--split [SPLIT]] [--output [OUTPUT]]
                       [--choose [n]]
                       [inputs [inputs ...]]

Detect P2P Botnet traffic using machine learning

positional arguments:
  inputs             Directory/file paths to search for input files

optional arguments:
  -h, --help         show this help message and exit
  --train            Use the input data to train and test a model
                     using the train-test split
  --retrain          Retrain the model using the preprocessed data
                     in the specified JSON file
  --csv              Use alternative modelling suitable for
                     dumping/loading pre-processed data in CSV file
  --validate         Use the input data to validate the pre-trained
                     model
  --predict          Predict class labels on the input data
  --dump             Save the preprocessed training data into JSON
                     format for reproducing results
  --split [SPLIT]    (only for --train) ratio of input data to use
                     for training (rest for testing)
  --output [OUTPUT]  (only for --predict) save the output to a file,
                     use "stdout" to print
  --choose [n]       Use only n randomly sampled files from the
                     input
```

### Particular examples of relevance
1. Classify the flows in the given PCAP file as 'Benign' or 'Botnet' and output a text file containing the results in the same directory (named as `<input_file_name>.out.txt`)
```
python3 botnetdetect.py file.pcap
```
2. Same as 1 but supply an output file ('stdout' for stdout)
```
python3 botnetdetect.py --output output.csv file.pcap
```
3. Same as 1 but read input files from many directories at once.
```
python3 botnetdetect.py data1/ data2/ data3/ data4/
```
4. Train the models on a given data set (labels deduced automatically), model is stored in `cache/` directory.
```
python3 botnetdetect.py --train data_set/
```
5. Choose the train-test split to be 70:30 during training.
```
python3 botnetdetect.py --train --split 0.7 data_set/
```
6. Train only on 10 PCAP files randomly sampled.
```
python3 botnetdetect.py --train --choose 10 data_set/
```
7. Validate the accuracy metrics of a model.
```
python3 botnetdetect.py --validate validation_set/
```
8. Dump the pre-processed extracted features into a JSON file for reproducibility. (CSV if --csv is specified alongside --dump)
```
python3 botnetdetect.py --dump data_set/
```
9. Retrain the model from preprocessed data read from a JSON file. (CSV if --csv is specified alongside --retrain)
```
python3 botnetdetect.py --retrain preprocessed.json
``` 
Note: `preprocessed.json` contains the pre-processed data we used to train our model. However it is present in compressed form in the submission as `preprocessed.7z`. Please decompress it to obtain `preprocessed.json`. `preprocessed.csv` contains pre-processed data for the csv-enabling model.
Note that training a model will overwrite the previous trained model. However, running the command below OR retraining with the preprocessed data should give the original (or equivalent) model again.

```
cp cache/model_bak.pickle cache/model.pickle
cp cache/model_csv_bak.pickle cache/model_csv.pickle
```

## Assumptions
Based on our understanding and research of the problem in the hand, we made the following assumptions (with reasons illustrated).

1. We define traffic in a network as being completely identified by a 2-tuple (src, dst) meaning all the packet exchanges (bidirectional) between any 2 nodes constitute a traffic flow. Here src and dst are whatever appear in the `source` and `destination` fields and may (in rare cases) be non-IPs. Note that this differs from the conventional definition of flow which is usually a 5 or 6-tuple. We make this simplification because it is as specified in the forum discussions, and it is also in the interest of simplicity, and it doesn't affect our performance.

2. Keeping with the spirit of the problem, we restrict our scope to the classification of P2P traffic only. Since P2P botnets rely on P2P traffic for communication and C&C, we conclude that non P2P traffic is irrelevant for classification purposes. That is, we discard all non P2P traffic from the PCAP files in the preprocessing stage. We do not take the attack phase of botnets into the consideration. (As an aside, from the nature of problems we observe that this forms the subject of problem 2 and therefore choose to confine our classification to P2P traffic only on the basis of the previous phases). These traffics will not be classified in the output.

3. We assume that the P2P traffic provided to us is homogeneous, i.e, in the data provided all P2P traffic in PCAP files corresponding to botnets is botnet-traffic and there is negligible minimal background P2P traffic in these files. This assumption is motivated by practical considerations of obtaining data and from our manual inspections. Usually data for botnet traffic is obtained from honeypots which only capture non-benign traffic. We take it that this was the case here as well. We take all P2P traffic in benign files to be benign as well, primarily because of quite low rate of botnets in normal networks.

So, our goal is to extract all 2-tuple traffic flows from a PCAP file and classify each such traffic flow to be benign or botnet traffic. For training the feature extraction (features are associated on a per flow basis) is done similarly and the assumption of homogenity allows us to obtain labels for each traffic and hence perform supervised learning.

## Feature Extraction

We extract features in 2 phases.

### Phase 1
In this phase we classify between P2P and non-P2P traffic in a PCAP file. To do this classification we rely on DNS queries and responses. The idea is that non-P2P communications usually involve a DNS query from the host whereas P2P communications usually directly happen without DNS resolution because IPs are known in advance. Thus, we extract all IPs found in DNS responses and all flows with source or destination IP in this set are classified as non-P2P and discarded before going into the next phase.

Note that this might also discard some P2P traffic. Because many P2P applications (including botnets) during the bootstrapping phase (when they start) communicate with some fixed domain names to obtain a starting set of peers. Our method will also classify this P2P traffic as non-P2P. However, from our experience, such flows are rare (usually the first few only) and for any PCAP file of good enough duration this should not hamper the accuracy in any measurable manner.

### Phase 2

In this phase we extract flows from the PCAP files. Note that our traffic flows are both bidirections and specified by a 2-tuple that is, protocol agnostic. We first of all discard all non-P2P flows (as described above using IPs found in DNS responses). Secondly for all P2P traffic flows thus obtained we extract a number of statistical features which may help in classifying between botnet traffic and benign traffic. Thus, our classification is statistical in nature. The other options were either port based classification or signature based classification. Both of these options are unsatisfactory because port numbers may vary on be non-standard as well as inspecting payload is both a time consuming operation, privacy-invading as well as payload may be encrypted limiting the inspection. The statistical features we use are:

1. number of packets

2. variance of the packet times

3. duration of the flow

4. sum of packet lengths

5. average packet length

6. variance of packet lengths

7. length of the first packet

8. symmetric correlation defined as |log((1+incoming_packets)/(1+outgoing_packets))|\*

9. symmetric length correlation defined as |log((1+sum_of_incoming_packet_lengths)/(1+sum_of_outgoing_packet_lengths))|\*

In our original modelling, for each traffic flow, we extract the above-mentioned features, but for each protocol that is seen (see sample.json for examples). So, the actual feature set is very large. We use feature dicts and sparse matrix in the model, which allows us to capture us the info about every protocol witnessed in the traffic flow, without being bogged down by the prohibisively large time and space complexities of having all these features represented explicitly.

In our alternative modelling to enable csv (which cannot use the great advantages of sparsity), we used the same features mentioned above, but without associating them with all seen protocols, thus making this approach protocol-agnostic.

However, we have found that having separate info for each protocol is very useful as which protocol is used, how often, etc. can be of great help in classification. This has also been confirmed empirically from the difference in the accuracy of our original protocol-aware feature modelling vs the csv-enabling protocol-agnostic feature modelling, however this restricts our generality of prediction given newer kinds of botnets, which have certain inherent differences.

\* The reason for the usage of absolute values of the logs is the following. The ratios are good indicators of the "response ratio", and the closer they are to 1, the better are the chances of the flow being benign. Also, since we are considering bidirectional flows, we need to have a symmetric function with respect to both ends. One more candidate was the larger of the ratio of the in and out parameters and its reciprocal. However this had two shortcomings - if there is a flow which has no response, then this characteristic blows up to infinity, and there is a high skew towards the higher ratios, which is not good for our model, and hence we used the log of this ratio. A good way to represent it is simply the absolute value of the log.

## Model

We have used an sklearn pipeline consisting of two parts: DictVectorizer and GradientBoostingClassifier. At the input end of the pipeline is a list of feature dicts where feature names are dict keys and feature values are dict values. The DictVectorizer converts the list of feature dicts to a sparse feature matrix and passes it on to GradientBoostingClassifier. The sparse feature matrix allows us to keep a lot of features without blowing up memory or time.

The choice of GradientBoostingClassifier is well thought-out. It has a training complexity which is linear in the number of training examples (and we have lots of those, on the order of 10^6 samples), is an ensemble learning technique and inherits the advantages of ensemble learning like less likelihood of overfitting, does not impose strict requirements on the data, and is robust, performant and accurate in general. Also, we were able to get really good results with it.

## Results
These results are for training with a 75% : 25% train-test split. Note that the models submitted were obtained by training on 100% of the data.

### Original model
```
Training model on 1468842 flows ...
Class Balance : 276856 vs 1191986
training time: 691.1389067173004 s
training time per traffic: 0.0004705331864947356 s

Evaluating model on 489614 flows ...
Class Balance : 92554 vs 397060
prediction time: 34.98868370056152 s
prediction time per traffic: 2.3820590438291882e-05 s
false positives: 1964 / 1468842
false negatives: 691 / 1468842
total mismatch: 2655 / 1468842
accuracy: 0.9981924536471588
f1 (micro): 0.9981924536471588
recall (micro): 0.9981924536471588
precision (micro): 0.9981924536471588
f1 (macro): 0.9970404731593268
recall (macro): 0.9961631773362736
precision (macro): 0.9979233379295962
```

### CSV enabling model
```
Training model on 1468842 flows ...
Class Balance : 276933 vs 1191909
training time: 677.4678580760956 s
training time per traffic: 0.0004612258214812046 s

Evaluating model on 489614 flows ...
Class Balance : 92477 vs 397137
prediction time: 186.5355429649353 s
prediction time per traffic: 0.00012699496812110172 s
false positives: 2214 / 1468842
false negatives: 1727 / 1468842
total mismatch: 3941 / 1468842
accuracy: 0.9973169340201329
f1 (micro): 0.9973169340201329
recall (micro): 0.9973169340201329
precision (micro): 0.9973169340201329
f1 (macro): 0.9956127030181323
recall (macro): 0.9952781751793947
precision (macro): 0.9959480414761256
```
