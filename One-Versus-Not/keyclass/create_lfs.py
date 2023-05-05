
import nltk

nltk.download('stopwords')
from nltk import download, pos_tag, corpus
import numpy as np
import pandas as pd
from scipy.spatial import distance
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
# from sklearn.semi_supervised import LabelPropagation
import torch
import models


def get_vocabulary(text_corpus, max_df=1.0, min_df=0.01, ngram_range=(1, 1)):
    """Returns vocabulary and word indicator matrix
    The word indicator matrix is a n x m matrix corresponding to n documents and m words in the
    vocabulary. 

    """
    # Vectorizing the vocabulary
    vectorizer = CountVectorizer(max_df=max_df,
                                 min_df=min_df,
                                 strip_accents='unicode',
                                 stop_words=corpus.stopwords.words('english'),
                                 ngram_range=ngram_range)

    word_indicator_matrix = vectorizer.fit_transform(text_corpus).toarray()
    vocabulary = np.asarray(vectorizer.get_feature_names_out())  # Vocabulary

    return word_indicator_matrix, vocabulary


def assign_categories_to_keywords(vocabulary,
                                  vocabulary_embeddings,
                                  label_embeddings,
                                  word_indicator_matrix,
                                  cutoff=None,
                                  topk=None,
                                  min_topk=True):

    assert ((cutoff is None) or (topk is None))

    distances = distance.cdist(vocabulary_embeddings, label_embeddings,
                               'cosine')

    dist_to_closest_cat = np.min(distances, axis=1)
    assigned_category = np.argmin(distances, axis=1)

    if cutoff is not None:
        # make mask based off of similarity score and cutoff
        mask = (dist_to_closest_cat <= cutoff).astype(bool)

    if topk is not None:
        # make mask based off of topk closest assigned category
        # WARNING could result on one class taking keywords from another class
        uniques = np.unique(assigned_category)
        mask = np.zeros(len(dist_to_closest_cat), dtype=bool)

        _, counts = np.unique(assigned_category, return_counts=True)
        print('Found assigned category counts', counts)
        if min_topk == True:
            topk = np.min([topk, np.min(counts)])

        for u in uniques:
            u_inds = np.where(assigned_category == u)[0]
            u_dists = dist_to_closest_cat[u_inds]
            sorted_inds = np.argsort(u_dists)[:topk]
            mask[u_inds[sorted_inds]] = 1

    keywords = vocabulary[mask]
    assigned_category = assigned_category[mask]
    word_indicator_matrix = word_indicator_matrix[:, np.where(mask)[0]]
    return keywords, assigned_category, word_indicator_matrix


def create_label_matrix(word_indicator_matrix, keywords, assigned_category):

    word_indicator_matrix = np.where(word_indicator_matrix == 0, -1, 0)
    for i in range(len(assigned_category)):
        word_indicator_matrix[:,
                              i] = np.where(word_indicator_matrix[:, i] != -1,
                                            assigned_category[i], -1)

    return pd.DataFrame(word_indicator_matrix, columns=keywords)


class CreateLabellingFunctions:
    """Class to create and store labelling functions.             
    """

    def __init__(self,
                 base_encoder='paraphrase-mpnet-base-v2',
                 device: torch.device = torch.device("cuda"),
                 label_model: str = 'data_programming'):

        self.device = device
        self.encoder = models.Encoder(model_name=base_encoder, device=device)

        self.label_matrix = None
        self.keywords = None
        self.word_indicator_matrix = None
        self.vocabulary = None
        self.vocabulary_embeddings = None
        self.assigned_category = None
        self.label_model_name = label_model

    def get_labels(self,
                   text_corpus,
                   label_names,
                   min_df,
                   ngram_range,
                   topk,
                   y_train,
                   label_model_lr,
                   label_model_n_epochs,
                   verbose=True,
                   n_classes=2):
        ## main driver function

        ## get the bert embeddings of the categories
        self.label_embeddings = self.encoder.encode(sentences=label_names)
        # print("Label Names = ",label_names)
        # print("Label embeddings = ",self.label_embeddings)

        ## get vocab according to n-grams
        self.word_indicator_matrix, self.vocabulary = get_vocabulary(\
            text_corpus=text_corpus,
            max_df=1.0,
            min_df=min_df,
            ngram_range=ngram_range)
        # print("Text corpus = ",text_corpus)
        # print("Word Indicator matrix = ",self.word_indicator_matrix)

        # embed vocab to compare with label_embeddings
        self.vocabulary_embeddings = self.encoder.encode(
            sentences=self.vocabulary)

        # print("Vocab = ",self.vocabulary)
        # print("Vocab embeddings = ",self.vocabulary_embeddings)
        # print('Label embeddings = ', self.label_embeddings)
        # print('w')

        # labeler.assign_categories_to_keywords(cutoff=0.9)
        self.keywords, self.assigned_category, self.word_indicator_matrix = assign_categories_to_keywords(\
            vocabulary=self.vocabulary,
            vocabulary_embeddings=self.vocabulary_embeddings,
            label_embeddings=self.label_embeddings,
            word_indicator_matrix=self.word_indicator_matrix,
            topk=topk)

        if verbose:
            print('labeler.vocabulary:\n', len(self.vocabulary))
            print('labeler.word_indicator_matrix.shape',
                  self.word_indicator_matrix.shape)

            print('Len keywords', len(self.keywords))
            print('assigned_category: Unique and Counts',
                  np.unique(self.assigned_category, return_counts=True))
            for u in range(len(label_names)):
                inds = np.where(self.assigned_category == u)[0]
                print(label_names[u], self.keywords[inds])

        self.label_matrix = create_label_matrix(\
            word_indicator_matrix=self.word_indicator_matrix,
            keywords=self.keywords,
            assigned_category=self.assigned_category)

            # print('labeler.label_matrix', np.unique(labeler.label_matrix, return_counts=True))
        label_model = models.LabelModelWrapper(\
            label_matrix=self.label_matrix,
            n_classes=n_classes,
            y_train=y_train,
            device=self.device,
            model_name=self.label_model_name)

        label_model.train_label_model(\
            lr=label_model_lr,
            n_epochs=label_model_n_epochs,
            cuda=True if torch.cuda.is_available() else False)

        proba_preds = label_model.predict_proba().values

        return proba_preds
