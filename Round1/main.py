from utility import *
import dynamic_analysis
import random

train_fraction = 0.75

train_validate_directory = './Dynamic_Analysis_Data_Part1'

static_files = []

for h, p, l in get(train_validate_directory, dynamics(all())):
    static_files.append((p, l))

train_validate_directory = './Dynamic_Analysis_Data_Part2'

for h, p, l in get(train_validate_directory, dynamics(all())):
    static_files.append((p, l))

random.shuffle(static_files)

zipped_train = static_files[:int(train_fraction * len(static_files))]
zipped_validate = static_files[len(zipped_train):]

train_files = []
train_labels = []
validate_files = []
validate_labels = []

for f, l in zipped_train:
    train_files.append(f)
    train_labels.append(l)

for f, l in zipped_validate:
    validate_files.append(f)
    validate_labels.append(l)

model = dynamic_analysis.DynamicModel()

# no need to train if the parameters are saved in string_analysis/model/
model.train(train_files, train_labels)

model.validate(validate_files, validate_labels)

