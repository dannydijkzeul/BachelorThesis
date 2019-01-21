# Copyright (c) 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

import os
import time
import json
import argparse
from collections import OrderedDict
import numpy as np
import torch

from src.utils import bool_flag, initialize_exp
from src.models import build_model
from src.trainer import Trainer
from src.evaluation import Evaluator

# TensorboardX
from tensorboardX import SummaryWriter


VALIDATION_METRIC = 'mean_cosine-csls_knn_10-S2T-10000'


# main
parser = argparse.ArgumentParser(description='Unsupervised training')
parser.add_argument("--seed", type=int, default=-1, help="Initialization seed")
parser.add_argument("--verbose", type=int, default=2, help="Verbose level (2:debug, 1:info, 0:warning)")
parser.add_argument("--exp_path", type=str, default="", help="Where to store experiment logs and models")
parser.add_argument("--exp_name", type=str, default="debug", help="Experiment name")
parser.add_argument("--exp_id", type=str, default="", help="Experiment ID")
parser.add_argument("--cuda", type=bool_flag, default=True, help="Run on GPU")
parser.add_argument("--export", type=str, default="txt", help="Export embeddings after training (txt / pth)")
# data
parser.add_argument("--src_lang", type=str, default='faroese', help="Source language")
parser.add_argument("--tgt_lang", type=str, default='en', help="Target language")
parser.add_argument("--emb_dim", type=int, default=300, help="Embedding dimension")
parser.add_argument("--max_vocab", type=int, default=200000, help="Maximum vocabulary size (-1 to disable)")
# mapping
parser.add_argument("--map_id_init", type=bool_flag, default=True, help="Initialize the mapping as an identity matrix")
parser.add_argument("--map_beta", type=float, default=0.001, help="Beta for orthogonalization")
# discriminator
parser.add_argument("--dis_layers", type=int, default=2, help="Discriminator layers")
parser.add_argument("--dis_hid_dim", type=int, default=2048, help="Discriminator hidden layer dimensions")
parser.add_argument("--dis_dropout", type=float, default=0., help="Discriminator dropout")
parser.add_argument("--dis_input_dropout", type=float, default=0.1, help="Discriminator input dropout")
parser.add_argument("--dis_steps", type=int, default=5, help="Discriminator steps")
parser.add_argument("--dis_lambda", type=float, default=1, help="Discriminator loss feedback coefficient")
parser.add_argument("--dis_most_frequent", type=int, default=75000, help="Select embeddings of the k most frequent words for discrimination (0 to disable)")
parser.add_argument("--dis_smooth", type=float, default=0.1, help="Discriminator smooth predictions")
parser.add_argument("--dis_clip_weights", type=float, default=0, help="Clip discriminator weights (0 to disable)")
# training adversarial
parser.add_argument("--adversarial", type=bool_flag, default=True, help="Use adversarial training")
parser.add_argument("--n_epochs", type=int, default=5, help="Number of epochs")
parser.add_argument("--epoch_size", type=int, default=1000000, help="Iterations per epoch")
parser.add_argument("--batch_size", type=int, default=32, help="Batch size")
parser.add_argument("--map_optimizer", type=str, default="sgd,lr=0.1", help="Mapping optimizer")
parser.add_argument("--dis_optimizer", type=str, default="sgd,lr=0.1", help="Discriminator optimizer")
parser.add_argument("--lr_decay", type=float, default=0.98, help="Learning rate decay (SGD only)")
parser.add_argument("--min_lr", type=float, default=1e-6, help="Minimum learning rate (SGD only)")
parser.add_argument("--lr_shrink", type=float, default=0.5, help="Shrink the learning rate if the validation metric decreases (1 to disable)")
# training refinement
parser.add_argument("--n_refinement", type=int, default=5, help="Number of refinement iterations (0 to disable the refinement procedure)")
# dictionary creation parameters (for refinement)
parser.add_argument("--dico_eval", type=str, default="default", help="Path to evaluation dictionary")
parser.add_argument("--dico_method", type=str, default='csls_knn_10', help="Method used for dictionary generation (nn/invsm_beta_30/csls_knn_10)")
parser.add_argument("--dico_build", type=str, default='S2T', help="S2T,T2S,S2T|T2S,S2T&T2S")
parser.add_argument("--dico_threshold", type=float, default=0, help="Threshold confidence for dictionary generation")
parser.add_argument("--dico_max_rank", type=int, default=15000, help="Maximum dictionary words rank (0 to disable)")
parser.add_argument("--dico_min_size", type=int, default=0, help="Minimum generated dictionary size (0 to disable)")
parser.add_argument("--dico_max_size", type=int, default=0, help="Maximum generated dictionary size (0 to disable)")
# reload pre-trained embeddings
parser.add_argument("--src_emb", type=str, default="", help="Reload source embeddings")
parser.add_argument("--tgt_emb", type=str, default="", help="Reload target embeddings")
parser.add_argument("--normalize_embeddings", type=str, default="", help="Normalize embeddings before training")

parser.add_argument("--validate_path", type=str, default="", help="Validation words")


# parse parameters
params = parser.parse_args()

# build model / trainer / evaluator
logger = initialize_exp(params)
src_emb, tgt_emb, mapping, discriminator = build_model(params, True)


trainer = Trainer(src_emb, tgt_emb, mapping, discriminator, params)
trainer.reload_best()
evaluator = Evaluator(trainer)


if params.validate_path == "":

    while True:
        word = raw_input("Query word: ")
        print word
        to_log2 = OrderedDict({'n_epoch': 0})
        evaluator.validate_words(to_log2, [word])
        print to_log2["Word_dict"].keys()
        for wordKey in to_log2["Word_dict"].keys():
            print to_log2["Word_dict"][wordKey]
else:

    en_words = []
    fa_words = []

    with open(params.validate_path, 'r') as r:
        words = r.readline()
        translateDict = {}
        while words:
            splitWord = words.split(",")

            translateDict[splitWord[0]] = splitWord[1].rstrip()
            en_words.append(splitWord[1].rstrip())
            fa_words.append(splitWord[0].rstrip())
            words = r.readline()


    to_log2 = OrderedDict({'n_epoch': 0})
    evaluator.validate_words(to_log2, fa_words)


    top1 = 0
    top5 = 0
    top10 = 0

    for translatedWord in to_log2["Word_dict"].keys():
        print translatedWord + " " + translateDict[translatedWord]
        translationEN = translateDict[translatedWord]
        transaltions = to_log2["Word_dict"][translatedWord][0:10]
        print transaltions
        try:
            indexTranslation = transaltions.index(translationEN)

            if indexTranslation == 0:
                top1 += 1

            if indexTranslation < 5:
                top5 += 1

            if indexTranslation < 10:
                top10 += 1
        except ValueError as e:
            pass




    print top1/float(len(to_log2["Word_dict"].keys()))
    print top5/float(len(to_log2["Word_dict"].keys()))
    print top10/float(len(to_log2["Word_dict"].keys()))
