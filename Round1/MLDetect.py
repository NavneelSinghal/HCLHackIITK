import sys
import random
import argparse
import utility
from string_analysis import StringModel
from dynamic_analysis import DynamicModel
from structure_analysis import StructureModel
from operator import itemgetter
from sklearn import metrics

default_string_model_sav = 'string_analysis/model/model.sav'
default_structure_model_sav = 'structure_analysis/model/model.sav'
default_dynamic_model_sav = 'dynamic_analysis/model/model.sav'

def map(func, iterable):
    ans = []
    for i in iterable:
        ans.append(func(i))
    return ans

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
             description='Detect malware using machine learning',
             allow_abbrev=True,
             epilog='''
             We can show some examples here
             ''')
    parser.add_argument(
            '--train',
            action='store_true',
            help='Use the input data to train the model'
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
            nargs=1,
            default=0.75,
            type=int,
            help='(only for train) train-test ratio to use'
    )
    parser.add_argument(
            '--model',
            nargs='?',
            choices=['all', 'string', 'structure', 'dynamic'],
            default='all',
            help='which models to use'
    )
    parser.add_argument(
            '--output',
            nargs='?',
            default='output.csv',
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
    for m in ['train', 'validate', 'predict']:
        if args[m]:
            mode = m
    inputs = args['inputs']
    if not inputs:
        try:
            inputs.append(input())
        except EOFError:
            pass

    def train_step(mod, files):
        files = list(filter(utility.labelled, files))
        random.shuffle(files) # remove later on
        training = files[:int(len(files)*args['split'])]
        validation = files[int(len(files)*args['split']):]
        mod.train(map(itemgetter(1), training), map(itemgetter(2), training))
        mod.validate(map(itemgetter(1), validation), map(itemgetter(2), validation))

    def validate_step(mod, files):
        files = list(filter(utility.labelled, files))
        mod.validate(map(itemgetter(1), files), map(itemgetter(2), files))

    def predict_step(mod, files):
        predictions = mod.predict(map(itemgetter(1), files))
        outfile = args['output']
        if outfile == 'stdout':
            outfile = sys.stdout
        else:
            outfile = open(outfile, 'w')
        for i, p in enumerate(predictions):
            pred = 'Malware'
            if p == 0:
                pred = 'Benign'
            print(f'{files[i][0]},{pred}', file=outfile)

    def ensemble(f1, f2, f3, p1, p2, p3):
        preds = {}
        actual = {}
        for i, f in enumerate(f2):
            h = f[0]
            l = f[2]
            if h in preds:
                preds[h].append(p2[i])
            else:
                preds[h] = [p2[i]]
                actual[h] = l and int(l > 0)
        for i, f in enumerate(f1):
            h = f[0]
            l = f[2]
            if h in preds:
                preds[h].append(p1[i])
            else:
                preds[h] = [p1[i]]
                actual[h] = l and int(l > 0)
        for i, f in enumerate(f3):
            h = f[0]
            l = f[2]
            if h in preds:
                preds[h].append(p3[i])
            else:
                preds[h] = [p3[i]]
                actual[h] = l and int(l > 0)

        hashes = []
        predictions = []
        labels = []
        for h, p in preds.items():
            for i in range(len(p)):
                p[i] = int(p[i] > 0)
            if len(p) == 3:
                pred = p[0]*p[1] + p[1]*p[2] + p[0]*p[2]
                pred = int(pred > 0)
            else:
                pred = p[-1]
                pred = int(pred > 0)
            hashes.append(h)
            predictions.append(pred)
            labels.append(actual[h])
        return (hashes, predictions, labels)

    model = args['model']
    if model == 'string':
        files = []
        for inp in inputs:
            files.extend(utility.get(inp, utility.strings()))
        if args['choose']:
            if len(files) > args['choose']:
                files = random.sample(files, args['choose'])
        print(f'Total {len(files)} String.txt(s) detected.')
        print(f'Loading string model ...')
        string_model = StringModel(default_string_model_sav)
        if mode == 'train':
            train_step(string_model, files)
        elif mode == 'validate':
            validate_step(string_model, files)
        else:
            predict_step(string_model, files)

    elif model == 'structure':
        files = []
        for inp in inputs:
            files.extend(utility.get(inp, utility.structures()))
        if args['choose']:
            if len(files) > args['choose']:
                files = random.sample(files, args['choose'])
        print(f'Total {len(files)} Structure_Info.txt(s) detected.')
        print(f'Loading structure model ...')
        structure_model = StructureModel(default_structure_model_sav)
        if mode == 'train':
            train_step(structure_model, files)
        elif mode == 'validate':
            validate_step(structure_model, files)
        else:
            predict_step(structure_model, files)

    elif model == 'dynamic':
        files = []
        for inp in inputs:
            files.extend(utility.get(inp, utility.dynamics()))
        if args['choose']:
            if len(files) > args['choose']:
                files = random.sample(files, args['choose'])
        print(f'Total {len(files)} JSON(s) detected.')
        print(f'Loading dynamic model ...')
        dynamic_model = DynamicModel(default_dynamic_model_sav)
        if mode == 'train':
            train_step(dynamic_model, files)
        elif mode == 'validate':
            validate_step(dynamic_model, files)
        else:
            predict_step(dynamic_model, files)

    else:
        string_files = []
        struct_files = []
        dynamc_files = []
        for inp in inputs:
            string_files.extend(utility.get(inp, utility.strings()))
            struct_files.extend(utility.get(inp, utility.structures()))
            dynamc_files.extend(utility.get(inp, utility.dynamics()))
        print(f'Total {len(string_files)} String.txt(s) detected.')
        print(f'Total {len(struct_files)} Structure_Info.txt(s) detected.')
        print(f'Total {len(dynamc_files)} JSON(s) detected.')
        print(f'Loading all 3 models ...')
        string_model = StringModel(default_string_model_sav)
        structure_model = StructureModel(default_structure_model_sav)
        dynamic_model = DynamicModel(default_dynamic_model_sav)

        if mode == 'train':
            if args['choose']:
                if len(string_files) > args['choose']:
                    string_files = random.sample(string_files, args['choose'])
                if len(struct_files) > args['choose']:
                    struct_files = random.sample(struct_files, args['choose'])
                if len(dynamc_files) > args['choose']:
                    dynamc_files = random.sample(dynamc_files, args['choose'])
            train_step(string_model, string_files)
            train_step(structure_model, struct_files)
            train_step(dynamic_model, dynamc_files)
        elif mode == 'validate':
            if args['choose']:
                print('The parameter "choose" is unavailable for this operation.'
                      'All files will be used.')
            string_files = list(filter(utility.labelled, string_files))
            struct_files = list(filter(utility.labelled, struct_files))
            dynamc_files = list(filter(utility.labelled, dynamc_files))
            res = ensemble(string_files, struct_files, dynamc_files,
                           string_model.predict(map(itemgetter(1), string_files)),
                           structure_model.predict(map(itemgetter(1), struct_files)),
                           dynamic_model.predict(map(itemgetter(1), dynamc_files)))
            # Write the sklearn step here please on x=res[1] and y=res[2]
            print("accuracy:\t\t\t", metrics.accuracy_score(res[1], res[2]))
            print("f1 score (micro):\t\t", metrics.f1_score(res[1], res[2], average = 'micro'))
            print("precision score (micro):\t", metrics.precision_score(res[1], res[2], average = 'micro'))
            print("recall score (micro):\t\t", metrics.recall_score(res[1], res[2], average = 'micro'))
            print("f1 score (macro):\t\t", metrics.f1_score(res[1], res[2], average = 'macro'))
            print("precision score (macro):\t", metrics.precision_score(res[1], res[2], average = 'macro'))
            print("recall score (macro):\t\t", metrics.recall_score(res[1], res[2], average = 'macro'))

        else:
            if args['choose']:
                print('The parameter "choose" is unavailable for this operation.'
                      'All files will be used.')
            res = ensemble(string_files, struct_files, dynamc_files,
                           string_model.predict(map(itemgetter(1), string_files)),
                           structure_model.predict(map(itemgetter(1), struct_files)),
                           dynamic_model.predict(map(itemgetter(1), dynamc_files)))

            outfile = args['output']
            if outfile == 'stdout':
                outfile = sys.stdout
            else:
                outfile = open(outfile, 'w')
            for i in range(len(res[0])):
                pred = 'Malware'
                if res[1][i] == 0:
                    pred = 'Benign'
                print(f'{res[0][i]},{pred}', file=outfile)

# from utility import *
# import string_analysis
# import random

# train_fraction = 0.75

# train_validate_directory = './Static_Analysis_Data'

# static_files = []

# for h, p, l in get(train_validate_directory, strings(all())):
#     static_files.append((p, l))

# random.shuffle(static_files)

# zipped_train = static_files[:int(train_fraction * len(static_files))]
# zipped_validate = static_files[len(zipped_train):]

# train_files = []
# train_labels = []
# validate_files = []
# validate_labels = []

# for f, l in zipped_train:
#     train_files.append(f)
#     train_labels.append(l)

# for f, l in zipped_validate:
#     validate_files.append(f)
#     validate_labels.append(l)

# model = string_analysis.StringModel()

# # no need to train if the parameters are saved in string_analysis/model/
# # model.train(train_files, train_labels)

# model.validate(validate_files, validate_labels)

