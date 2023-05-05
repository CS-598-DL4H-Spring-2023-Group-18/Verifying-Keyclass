import sys

sys.path.append('../keyclass/')

import utils
import models
import create_lfs
import numpy as np
import pickle
import argparse
import torch
import os
from os.path import join, exists

def label_converter(args, inp):
    # print("Inside Label Converter")
    # print("Arg",args['n_class_being_tested'])
    return_val = []
    for line in inp:
        row = []
        for c in line:
            if c=='0' or c=='1':
                row.append(int(c))
        # return_val.append(row)
        # print(row, row[args['n_class_being_tested']])
        return_val.append(row[args['n_class_being_tested']])
    return np.array(return_val)


def run(args_cmd):

    args = utils.Parser(config_file_path=args_cmd.config).parse()
    print(args)

    # Load training data
    train_text = utils.fetch_data(dataset=args['dataset'],
                                  path=args['data_path'],
                                  split='train')[:args['size_of_dataset']]

    training_labels_present = False
    if exists(join(args['data_path'], args['dataset'], 'train_labels.txt')):
        with open(join(args['data_path'], args['dataset'], 'train_labels.txt'),
                  'r') as f:
            y_train = f.readlines()[:args['size_of_dataset']]

        # y_train = np.array([int(i.replace('\n', '')) for i in y_train])
        # print("YTRAIN = ",y_train)
        y_train = label_converter(args, y_train)
        # print("YTRAIN = ", y_train)
        training_labels_present = True
    else:
        y_train = None
        training_labels_present = False
        print('No training labels found!')

    with open(join(args['data_path'], args['dataset'], 'train_embeddings.pkl'),
              'rb') as f:
        X_train = pickle.load(f)

    # Print dataset statistics
    print(f"Getting labels for the {args['dataset']} data...")
    print(f'Size of the data: {len(train_text)}')
    if training_labels_present:
        print('Class distribution', np.unique(y_train, return_counts=True))

    # Load label names/descriptions
    label_names = []
    for a in args:
        if 'target' in a: label_names.append(args[a])

    label_names = [label_names[args['n_class_being_tested']]]
    # print("Label Names",label_names)

    # Creating labeling functions
    labeler = create_lfs.CreateLabellingFunctions(
        base_encoder=args['base_encoder'],
        device=torch.device(args['device']),
        label_model=args['label_model'])

    # print("YTRAIN",y_train)
    # print("TRAIN TEXT",train_text)
    # print("LABEL NAMES",label_names)
    proba_preds = labeler.get_labels(
        text_corpus=train_text,
        label_names=label_names,
        min_df=args['min_df'],
        ngram_range=args['ngram_range'],
        topk=args['topk'],
        y_train=y_train,
        label_model_lr=args['label_model_lr'],
        label_model_n_epochs=args['label_model_n_epochs'],
        verbose=True,
        n_classes=args['n_classes'])

    y_train_pred = proba_preds

    # Save the predictions
    if not os.path.exists(args['preds_path']): os.makedirs(args['preds_path'])
    with open(
            join(args['preds_path'], f"{args['label_model']}_proba_preds.pkl"),
            'wb') as f:
        pickle.dump(proba_preds, f)

    # Print statistics
    print('Label Model Predictions: Unique value and counts',
          np.unique(y_train_pred, return_counts=True))
    if training_labels_present:
        print('Label Model Training Accuracy',
              np.mean(y_train_pred == y_train))

        # Log the metrics
        training_metrics_with_gt = utils.compute_metrics(
            y_preds=y_train_pred, y_true=y_train, average=args['average'])
        utils.log(metrics=training_metrics_with_gt,
                  filename='label_model_with_ground_truth',
                  results_dir=args['results_path'],
                  split='train',
                  class_being_tested=str(args['n_class_being_tested']))


# if __name__ == "__main__":
#     parser_cmd = argparse.ArgumentParser()
#     parser_cmd.add_argument('--config', default='../default_config.yml', help='Configuration file')
#     args_cmd = parser_cmd.parse_args()

#     run(args_cmd)
