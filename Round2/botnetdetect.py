#!/usr/bin/env python3

import sys
import time
import json
import random
import argparse
import os
from pathlib import Path
from backend import get_feature_dict
from operator import itemgetter
import model

def map(func, iterable):
    ans = []
    for i in iterable:
        ans.append(func(i))
    return ans

def scan_files(root):
    labels = {'benign': 0, 'botnet': 1}
    formats = ['a1b2c3d4', 'd4c3b2a1', '0a0d0d0a']
    files = []
    def scan(path, label):
        if path.is_file():
            with open(path, 'rb') as f:
                byt = f.read(4)
            if byt.hex() in formats:
                if not label:
                    if 'Benign' in path.parts:
                        label = 0
                    elif 'Botnet' in path.parts:
                        label = 1
                files.append((label, str(path)))
        else:
            if path.name.lower() in labels:
                label = labels[path.name.lower()]
            for subpath in path.iterdir():
                scan(subpath, label)

    root = Path(root)
    if not root.exists():
        print(f'WARNING: Check path {root} if it exists.')
        return None
    scan(root, None)
    return files

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
             description='Detect P2P Botnet traffic using machine learning',
             allow_abbrev=True,
             epilog=''
    )
    parser.add_argument(
            '--train',
            action='store_true',
            help='Use the input data to train and test a model using the train-test split'
    )
    parser.add_argument(
            '--retrain',
            action='store_true',
            help='Retrain the model using the preprocessed data in the specified JSON file'
    )
    parser.add_argument(
            '--csv',
            action='store_true',
            help='Use alternative modelling suitable for dumping/loading pre-processed data in CSV file'
    )
    parser.add_argument(
            '--validate',
            action='store_true',
            help='Use the input data to validate the pre-trained model'
    )
    parser.add_argument(
            '--predict',
            action='store_true',
            help='Predict class labels on the input data'
    )
    parser.add_argument(
            '--dump',
            action='store_true',
            help='Save the preprocessed training data into JSON format for reproducing results'
    )
    parser.add_argument(
            '--split',
            nargs='?',
            default=0.75,
            type=float,
            help='(only for --train) ratio of input data to use for training (rest for testing)'
    )
    parser.add_argument(
            '--output',
            nargs='?',
            default=None,
            help='(only for --predict) save the output to a file, use "stdout" to print'
    )
    parser.add_argument(
            '--choose',
            nargs='?',
            default=0,
            metavar='n',
            type=int,
            help='Use only n randomly sampled files from the input'
    )
    parser.add_argument(
            'inputs',
            nargs='*',
            help='Directory/file paths to search for input files'
    )
    args = vars(parser.parse_args())
    #print(args)
    mode = 'predict'
    for m in ['train', 'retrain', 'validate', 'predict', 'dump']:
        if args[m]:
            mode = m
    inputs = args['inputs']
    if not inputs:
        try:
            while True:
                inputs.append(input())
        except EOFError:
            pass

    if mode == 'retrain':
        if args['csv']:
            print('loading from', inputs[0], '...', end='\r')
            start = time.time()
            D, y = model.load_D_y_from_csv(inputs[0])
            finish = time.time()
            print('pre-processed data loaded from', inputs[0], 'in:', finish-start, 's')
            print('training...', end='\r')
            start = time.time()
            clf = model.get_trained_classifier(D, y, 'cache/')
            finish = time.time()
            print('training time:', finish-start, 's')
            exit()
        else:
            print('loading from', inputs[0], '...', end='\r')
            start = time.time()
            with open(inputs[0], 'r') as save:
                loaded = json.load(save)
            finish = time.time()
            print('pre-processed data loaded from', inputs[0], 'in:', finish-start, 's')
            flows, labels, ids = [], [] , []
            for record in loaded:
                labels.append(record['label'])
                flows.append(record['traffic'])
            mode = 'train'
            ids = [None] * len(labels)

            zipped = list(zip(flows, labels, ids))
            random.shuffle(zipped)
            training_data = zipped
            print(f'\nTraining model on {len(training_data)} flows ...')
            clf = model.get_trained_classifier(
                    map(itemgetter(0), training_data),
                    map(itemgetter(1), training_data),
                    'cache/')
            exit()

    else:
        print('Scanning for PCAP files ...')
        files = []
        for inp in inputs:
            files.extend(scan_files(inp))

        print(f'Found {len(files)} PCAP/PCAPNG files.\n')
        if args['choose']:
            if args['choose'] < len(files):
                files = random.sample(files, args['choose'])
            print(f"Choosing {args['choose']} random PCAP/PCAPNG files for operation")

        cache = Path('cache/')
        if not cache.exists():
            cache.mkdir()

        print('Start feature extraction ...')
        flows, labels, ids = [], [] , []
        for (i,f) in enumerate(files):
            print (f'({i+1}/{len(files)}) Now Parsing {f[1]} -- {str(f[0])+(" (Benign)" if f[0]==0 else " (Botnet)")}')
            try:
                _flows, _ids = get_feature_dict(f[1], 'cache/', ignore_protocols=args['csv'])
                flows.extend(_flows)
                ids.extend(_ids)
                labels.extend([f[0]] * len(_flows))
            except BaseException as e:
                print(f'CRITICAL: Parsing Error on file {f} : {str(e)}')
        print('Feature extraction complete!\n')
        del files

    if mode == 'dump':
        if args['csv']:
            f = 'preprocessed.csv'
            print('dumping preprocessed data in', f, '...', end='\r')
            start = time.time()
            model.output_csv(flows, labels, f)
            finish = time.time()
            print('dumped preprocessed data in', f, 'in:', finish-start, 's')
            exit()
        else:
            print('dumping preprocessed data in preprocessed.json ...', end='\r')
            start = time.time()
            dump_data = []
            for f,l,i in zip(flows,labels,ids):
                record = {
                        'label': l,
                        'src': i[0],
                        'dst': i[1],
                        'traffic': f
                }
                dump_data.append(record)
            with open('preprocessed.json', 'w') as save:
                json.dump(dump_data, save)
            finish = time.time()
            print('dumped preprocessed data in preprocessed.json in:', finish-start, 's')
            exit()

    def class_balance(labs):
        cnt0, cnt1 = 0, 0
        for l in labs:
            if l == 1:
                cnt1 += 1
            elif l == 0:
                cnt0 += 1
            else:
                print('Failed to detect some labels')
        print(f'Class Balance : {cnt0} vs {cnt1}')

    if mode == 'train':
        zipped = list(zip(flows, labels, ids))
        random.shuffle(zipped)
        training_data = zipped[:int(args['split'] * len(zipped))]
        test_data = zipped[len(training_data):]
        print(f'\nTraining model on {len(training_data)} flows ...')
        class_balance(map(itemgetter(1), training_data))
        clf = model.get_trained_classifier(
                map(itemgetter(0), training_data),
                map(itemgetter(1), training_data),
                'cache/')

        print(f'\nEvaluating model on {len(test_data)} flows ...')
        class_balance(map(itemgetter(1), test_data))
        predictions = model.predict(clf, map(itemgetter(0), training_data))
        model.print_metrics(
                map(itemgetter(1), training_data),
                predictions)
        exit()

    elif mode == 'validate':
        if args['csv']:
            clf = model.load_trained_classifier('cache/', csv_model=True)
        else:
            clf = model.load_trained_classifier('cache/')
        if not clf:
            raise ValueError('No trained classifier found to load!')
        class_balance(labels)
        predictions = model.predict(clf, flows)
        model.print_metrics(labels, predictions)
        exit()

    elif mode == 'predict':
        if args['csv']:
            clf = model.load_trained_classifier('cache/', csv_model=True)
        else:
            clf = model.load_trained_classifier('cache/')
        if not clf:
            raise ValueError('No trained classifier found to load!')
        predictions = model.predict(clf, flows)
        outfile = args['output']
        if outfile is None:
            outfile = os.path.split(inputs[0])[1] + '.out.txt'
            print('Output dumped in:', outfile)
        if outfile == 'stdout':
            outfile = sys.stdout
        else:
            outfile = open(outfile, 'w')
        for i in range(len(predictions)):
            if predictions[i] == 0:
                pred = 'Benign'
            elif predictions[i] == 1:
                pred = 'Botnet'
            print(f'{ids[i]}\t{pred}', file=outfile)
        outfile.close()
