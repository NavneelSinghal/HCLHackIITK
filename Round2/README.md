# P2P Botnet Detection using Machine Learning
In this round, we implemented p2p botnet traffic detection using machine learning techniques.
## Installation
1. The tool uses tshark (wireshark's packet dissector) as the parsing engine to read PCAP/PCAPNG files. Therefore you must have tshark installed.

For Ubuntu -
```
sudo apt install tshark
```
for Mac -
```
brew install tshark
```
for Windows -
It comes with [wireshark installer](https://www.wireshark.org/#download).

Make sure the tshark binary is added to the PATH environment variable.

2. (Optional) Set up a virtual environment On linux
```
python3 -m venv env
source env/bin/activate
```
3. Install the necessary python libraries
```
python3 -m pip install -r requirements.txt
```
## Usage
Full specification
```
usage: MalwareDetection.py [-h] [--train] [--validate] [--predict]
                           [--split [SPLIT]]
                           [--model [{all,string,structure,dynamic}]]
                           [--output [OUTPUT]] [--choose [n]]
                           [inputs [inputs ...]]

Detect malware using machine learning

positional arguments:
  inputs                Directories to search for input files

optional arguments:
  -h, --help            show this help message and exit
  --train               Use the input data to train the model
  --validate            Use the input data to validate the model
  --predict             Predict output on the input data
  --split [SPLIT]       (only for train) train-total data ratio to use
  --model [{all,string,structure,dynamic}]
                        which model to use (default is all)
  --output [OUTPUT]     (only for predict) save the output to a file, use
                        stdout to print
  --choose [n]          Use only n randomly sampled files from the input

```
### Examples
1. Make predictions on a PCAP file
```
python3 botnet.py file.pcap
```
2. Redirect the output to a file
```
python3 botnet.py --output output.csv file.pcap
```
3. Read input files from many directories at once.
```
python3 botnet.py data1/ data2/ data3/ data4/
```
4. Train the models on a given data set (labels deduced automatically).
```
python3 botnet.py --train data_set/
```
5. Choose the train-test split to be 70:30 during training.
```
python3 botnet.py --train --split 0.7 data_set/
```
6. Train only on 10 PCAP files randomly sampled.
```
python3 botnet.py --train --choose 10 data_set/
```
7. Validate the accuracy metrics of a model again.
```
python3 botnet.py --validate validation_set/
```
8. Dump the pre-processed extracted features into a CSV file for reproducability.
```
python3 botnet.py --dump data_set/
```
9. Retrain the model from feature vectors read from the dumped CSV file
```
python3 botnet.py --retrain preprocessed.csv
``` 

Note that training a model will overwrite the previous trained model. In any case if you want to restore to default pre-trained model run the following commands.
```
python3 botnet.py --retrain original_data.csv
```

## Assumptions
Based on our understanding and research of the problem in the hand, we made the following assumptions (with reasons illustrated) keeping in mind time and resource constraints.

1. We define traffic in a network as being completely identified by a 2-Tuple (src_ip, dst_ip) meaning all the packet exchanges (bidirectional) between any 2 nodes constitute a traffic flow. Note that this differs from the conventional definition of flow which is usually a 5 or 6-Tuple. We make this simplification partly owing to time constraints and partly due to some practical considerations in the parsing engine. The assumption will seem justified with the results obtained.

2. Only P2P botnets (and traffic) are to be classified. Since P2P botnets rely on P2P traffic for communication and C&C, we conclude that non p2p traffic is irrelevant for classification purposes. That is, we discard all non p2p traffic from the PCAP files in the preprocessing stage. This has certain other implications such as not being able to take attack phase of botnets into the consideration but from the nature of problems we observe that this forms the subject of problem 2 and therefore choose to confine our classification to p2p traffic only.

3. The P2P traffic provided to us is homogenous. Meaning, in the data provided all p2p traffic in PCAP files corresponding to botnets is botnet-traffic and there is no other (or minimal) background p2p traffic in these files. This assumption is motivated by practical considerations of obtaining data and from our manual inspections. Usually data for botnet traffic is obtained from honey nets which only capture non-benign traffic. We take it that this was the case here as well. Note that we take all p2p traffic in benign files to be benign as well (no intermixing).

Henceforth, the goal of this solution is to extract all 2-Tuple traffic flows from a PCAP file and classify each such traffic flow to be benign or botnet traffic. For training the feature extraction (features are associated on a per flow basis) is done similarly and the assumption of homogenity allows us to obtain labels for each traffic and hence perform supervised learning.

## Feature Extraction

We extract features in 2 phases.

### Phase 1
In this phase we classify between p2p and non-p2p traffic in a PCAP file. To do this classification we rely on DNS queries and responses. The idea is that non-p2p communications usually involve a DNS query from the host whereas p2p communications usually directly happen without DNS resolution because IPs are known in advance. Thus, we extract all IPs found in DNS responses and all flows with source or destination IP in this set are classified as non-p2p and discarded before going into the next phase.

Note that this might also discard some p2p traffic. Because many p2p applications (including botnets) during the bootstrapping phase (when they start) communicate with some fixed domain names to obtain a starting set of peers. Our classifier will also classify this p2p traffic as non-p2p. However, in our experience such flows are rare (usually the first few only) and for any PCAP file of good enough duration this should not hamper the accuracy.

### Phase 2

In this phase we extract flows from the PCAP files. Note that our traffic flows are both bidirections and specified by a 2-Tuple that is, protocol agnostic. We first of all discard all non-p2p flows (as described above using IPs found in DNS responses). Secondly for all p2p traffic flows thus obtained we extract a number of statistical features which may help in classifying between botnet traffic and benign traffic. Thus, our classification is statistical in nature. The other options were either port based classification or signature based classification. Both of these options are unsatisfactory because port numbers may vary on be non-standard as well as inspecting payload is both a time consuming operation, privacy-invading as well as payload may be encrypted limiting the inspection. Thus, our statistical features include -

** LIST OF ALL FEATURES HERE **

### Obtaining Labels

The problem deals with classifying traffic flows but obviously the data is unlabelled (wrt traffic flows). This naturally poses a problem and without simplifications requires unsupervised learning. However under practical considerations as explained above we make the homogenity assumption and therefore we conclude labels of the traffic flows are same as labels of the PCAP file.

## Model

Explain the model here

## Results

### Standard Tests

### Novelty Tests
