import sys
import random
import argparse
import traceback
from tqdm import tqdm
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
             epilog='''
            Show some usage examples here
             ''')
    parser.add_argument(
            '--train',
            action='store_true',
            help='Use the input data to train the model'
    )
    parser.add_argument(
            '--retrain',
            action='store_true',
            help='Retrain the model using feature vectors in CSV file'
    )
    parser.add_argument(
            '--validate',
            action='store_true',
            help='Use the input data to validate the model'
    )
    parser.add_argument(
            '--predict',
            action='store_true',
            help='Predict output on the input data'
    )
    parser.add_argument(
            '--split',
            nargs='?',
            default=0.75,
            type=float,
            help='(only for train) train-total data ratio to use'
    )
    parser.add_argument(
            '--output',
            nargs='?',
            default='stdout',
            help='(only for predict) save the output to a file, use stdout to print'
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
            help='Directories to search for input files'
    )
    args = vars(parser.parse_args())
    print(args)
    mode = 'predict'
    for m in ['train', 'retrain', 'validate', 'predict']:
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
        print('Re-training not implemented')
        exit()

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
        print (f'({i}/{len(files)}) Now Parsing {f[1]} -- {f[0]}')
        try:
            _flows, _ids = get_feature_dict(f[1], 'cache/')
            flows.extend(_flows)
            ids.extend(_ids)
            labels.extend([f[0]] * len(_flows))
        except BaseException as e:
            print(f'CRITICAL: Parsing Error on file {f}')
            traceback.print_exc()
    print('Feature extraction complete!\n')
    del files

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

    elif mode == 'validate':
        clf = model.load_trained_classifier('cache/')
        if not clf:
            raise ValueError('No trained classifier found to load!')
        class_balance(labels)
        predictions = model.predict(clf, flows)
        model.print_metrics(labels, predictions)

    elif mode == 'predict':
        clf = model.load_trained_classifier('cache/')
        if not clf:
            raise ValueError('No trained classifier found to load!')
        predictions = model.predict(clf, flows)
        outfile = args['output']
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
