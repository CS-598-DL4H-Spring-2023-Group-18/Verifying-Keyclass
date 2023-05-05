
import json
from os.path import join, exists
import re
from typing import List, Dict, Tuple, Iterable, Type, Union, Callable, Optional
import numpy as np
import joblib
from sklearn.metrics import precision_score, recall_score, roc_auc_score, roc_curve, precision_recall_curve, accuracy_score, precision_recall_fscore_support
from datetime import datetime
import torch
from yaml import load, dump
from yaml import CLoader as Loader, CDumper as Dumper


def log(metrics: Union[List, Dict], filename: str, results_dir: str,
        split: str, class_being_tested: str):
    """Logging function
        
        Parameters
        ----------
        metrics: Union[List, Dict]
            The metrics to log and save in a file
        filename: str
            Name of the file
        results_dir: str
            Path to results directory
        split: str
            Train/test split
        class_being_tested: str
            Class being tested
    """
    if isinstance(metrics, list):
        # assert len(metrics) == 3, "Metrics must be of length 3!"
        results = dict()
        results['F1'] = metrics[0]
        results['Precision'] = metrics[1]
        results['Accuracy'] = metrics[2]
        results['Recall'] = metrics[3]
        results['Theta'] = metrics[4]
        results['F1_Default'] = metrics[5]
        results['Precision_Default'] = metrics[6]
        results['Accuracy_Default'] = metrics[7]
        results['Recall_Default'] = metrics[8]

    elif isinstance(metrics, np.ndarray):
    #     # assert len(metrics) == 3, "Metrics must be of length 3!"
        results = dict()
        results['F1 (mean, std)'] = metrics[0].tolist()
        results['Precision (mean, std)'] = metrics[1].tolist()
        results['Accuracy (mean, std)'] = metrics[2].tolist()
        results['Recall (mean, std)'] = metrics[3].tolist()
        results['Theta (mean, std)'] = metrics[4].tolist()
        results['F1_Default (mean, std)'] = metrics[5].tolist()
        results['Precision_Default (mean, std)'] = metrics[6].tolist()
        results['Accuracy_Default (mean, std)'] = metrics[7].tolist()
        results['Recall_Default (mean, std)'] = metrics[8].tolist()
    else:
        results = metrics

    filename_complete = join(
        results_dir,
        f'{class_being_tested}_{split}_{filename}_{datetime.now().strftime("%d-%b-%Y-%H_%M_%S")}.txt'
    )
    print(f'Saving results in {filename_complete}...')
    print(results)

    with open(filename_complete, 'w', encoding='utf-8') as f:
        f.write(json.dumps(results))


def compute_metrics(y_preds: np.array,
                    y_true: np.array,
                    average: str = 'weighted'):
    """Compute accuracy, recall and precision

        Parameters
        ----------
        y_preds: np.array
            Predictions
        
        y_true: np.array
            Ground truth labels
        
        average: str
            This parameter is required for multiclass/multilabel targets. If None, 
            the scores for each class are returned. Otherwise, this determines the 
            type of averaging performed on the data.
    """
    y_preds = np.asarray(y_preds).reshape((1,-1)).squeeze()
    y_preds_default = (y_preds>0.5).astype(int).tolist()
    y_preds = y_preds.tolist()
    y_true = np.asarray(y_true).reshape((1,-1)).squeeze()
    y_true = y_true.tolist()
    auc_score = roc_auc_score(y_true,y_preds)
    precision, recall, threshold = precision_recall_curve(y_true, y_preds)
    f1_scores = 2 * recall * precision / (recall + precision)
    deno = recall + precision
    f1_scores = np.where(deno <= 0, 0, f1_scores)
    # print("F1 scores", f1_scores)
    # print("precision",precision)
    # print("recall",recall)
    # print("threshold",threshold)
    best_id = np.argmax(f1_scores)
    # print("best id", best_id)
    theta = threshold[best_id]
    F1 = f1_scores[best_id]
    prec = precision[best_id]
    rec = recall[best_id]
    # print("theta", theta, F1, prec, rec)
    acc = accuracy_score(y_true, (y_preds>theta).astype(int))
    # print("Acc",acc)

    prec2, rec2, f1_2, _ = precision_recall_fscore_support(y_true, y_preds_default, average=average)
    acc2 = accuracy_score(y_true, y_preds_default)

    return [
        F1,
        prec,
        acc,
        rec,
        theta,
        f1_2,
        prec2,
        acc2,
        rec2
    ]


def compute_metrics_bootstrap(y_preds: np.array,
                              y_true: np.array,
                              average: str = 'weighted',
                              n_bootstrap: int = 100,
                              n_jobs: int = 10):
    """Compute bootstrapped confidence intervals (CIs) around metrics of interest. 

        Parameters
        ----------
        y_preds: np.array
            Predictions
        
        y_true: np.array
            Ground truth labels
        
        average: str
            This parameter is required for multiclass/multilabel targets. If None, 
            the scores for each class are returned. Otherwise, this determines the 
            type of averaging performed on the data.

        n_bootstrap: int
            Number of boostrap samples to compute CI. 

        n_jobs: int
            Number of jobs to run in parallel. 
    """
    print("Inside compute metrics bootstrap")
    output_ =  joblib.Parallel(n_jobs=n_jobs, verbose=1)(
                                joblib.delayed(compute_metrics)
                                    (y_preds[boostrap_inds], y_true[boostrap_inds]) \
                                    for boostrap_inds in [\
                                    np.random.choice(a=len(y_true), size=len(y_true)) for k in range(n_bootstrap)])
    output_ = np.array(output_)
    means = np.mean(output_, axis=0)
    stds = np.std(output_, axis=0)
    return np.stack([means, stds], axis=1)


def get_balanced_data_mask(proba_preds: np.array,
                           max_num: int = 7000,
                           class_balance: Optional[np.array] = None):
    """Utility function to keep only the most confident predictions, while maintaining class balance

        Parameters
        ---------- 
        proba_preds: Probabilistic labels of data points
        max_num: Maximum number of data points per class
        class_balance: Prevalence of each class

    """
    if class_balance is None:  # Assume all classes are equally likely
        class_balance = np.ones(proba_preds.shape[1]) / proba_preds.shape[1]

    assert np.sum(
        class_balance
    ) - 1 < 1e-3, "Class balance must be a probability, and hence sum to 1"
    assert len(class_balance) == proba_preds.shape[
        1], f"Only {proba_preds.shape[1]} classes in the data"

    # Get integer of max number of elements per class
    class_max_inds = [int(max_num * c) for c in class_balance]
    train_idxs = np.array([], dtype=int)

    for i in range(proba_preds.shape[1]):
        sorted_idxs = np.argsort(
            proba_preds[:, i])[::-1]  # gets highest probas for class
        sorted_idxs = sorted_idxs[:class_max_inds[i]]
        print(
            f'Confidence of least confident data point of class {i}: {proba_preds[sorted_idxs[-1], i]}'
        )
        train_idxs = np.union1d(train_idxs, sorted_idxs)

    mask = np.zeros(len(proba_preds), dtype=bool)
    mask[train_idxs] = True
    return mask


def clean_text(sentences: Union[str, List[str]]):
    """Utility function to clean sentences
    """
    if isinstance(sentences, str):
        sentences = [sentences]

    for i, text in enumerate(sentences):
        text = text.lower()
        text = re.sub(r'<.*?>|[\.`\',;\?\*\[\]\(\)-:_]*|[0-9]*', '', text)
        text = re.sub(r'[\r\n]+', ' ', text)
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)
        sentences[i] = text

    return sentences


def fetch_data(dataset='imdb', path='~/', split='train'):
    """Fetches a dataset by its name

	    Parameters
	    ---------- 
	    dataset: str
	        List of text to be encoded. 

	    path: str
	        Path to the stored data. 

	    split: str
	        Whether to fetch the train or test dataset. Options are one of 'train' or 'test'. 
    """
    #_dataset_names = ['agnews', 'amazon', 'dbpedia', 'imdb', 'mimic']
    #if dataset not in _dataset_names:
    #    raise ValueError(f'Dataset must be one of {_dataset_names}, but received {dataset}.')
    #if split not in ['train', 'test']:
    #    raise ValueError(f'split must be one of \'train\' or \'test\', but received {split}.')

    if not exists(f"{join(path, dataset, split)}.txt"):
        raise ValueError(
            f'File {split}.txt does not exists in {join(path, dataset)}')

    text = open(f'{join(path, dataset, split)}.txt').readlines()

    # if dataset == 'mimic':
    #     text = [cleantext(line) for line in text]

    return text


def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[
        0]  #First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(
        token_embeddings.size()).float()

    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(
        input_mask_expanded.sum(1), min=1e-9)


def _text_length(text: Union[List[int], List[List[int]]]):
    """
    Help function to get the length for the input text. Text can be either
    a list of ints (which means a single text as input), or a tuple of list of ints
    (representing several text inputs to the model).

    Adapted from https://github.com/UKPLab/sentence-transformers/blob/40af04ed70e16408f466faaa5243bee6f476b96e/sentence_transformers/SentenceTransformer.py#L548
    """

    if isinstance(text, dict):  #{key: value} case
        return len(next(iter(text.values())))
    elif not hasattr(text, '__len__'):  #Object has no len() method
        return 1
    elif len(text) == 0 or isinstance(text[0],
                                      int):  #Empty string or list of ints
        return len(text)
    else:
        return sum([len(t)
                    for t in text])  #Sum of length of individual strings


class Parser:

    def __init__(
            self,
            config_file_path='../config_files/default_config.yml',
            default_config_file_path='../config_files/default_config.yml'):
        """Class to read and parse the config.yml file
		"""
        self.config_file_path = config_file_path
        with open(default_config_file_path, 'rb') as f:
            self.default_config = load(f, Loader=Loader)

    def parse(self):
        with open(self.config_file_path, 'rb') as f:
            self.config = load(f, Loader=Loader)

        for key, value in self.default_config.items():
            if ('target' not in key) and ((key not in list(self.config.keys()))
                                          or (self.config[key] is None)):
                self.config[key] = self.default_config[key]
                print(
                    f'Setting the value of {key} to {self.default_config[key]}!'
                )

        target_present = False
        for key in self.config.keys():
            if 'target' in key:
                target_present = True
                break
        if not target_present: raise ValueError("Target must be present.")
        self.save_config()
        return self.config

    def save_config(self):
        with open(self.config_file_path, 'w') as f:
            dump(self.config, f)
