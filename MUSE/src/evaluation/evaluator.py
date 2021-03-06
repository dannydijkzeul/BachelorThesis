#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2017-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
#

from logging import getLogger
from copy import deepcopy
import numpy as np
from torch.autograd import Variable
from torch import Tensor as torch_tensor

from . import get_wordsim_scores, get_crosslingual_wordsim_scores, get_wordanalogy_scores
from . import get_word_translation_accuracy
from . import load_europarl_data, get_sent_translation_accuracy
from ..dico_builder import get_candidates, build_dictionary
from src.utils import get_idf






logger = getLogger()


class Evaluator(object):

    def __init__(self, trainer):
        """
        Initialize evaluator.
        """
        self.src_emb = trainer.src_emb
        self.tgt_emb = trainer.tgt_emb
        self.src_dico = trainer.src_dico
        self.tgt_dico = trainer.tgt_dico
        self.mapping = trainer.mapping
        self.discriminator = trainer.discriminator
        self.params = trainer.params

    def monolingual_wordsim(self, to_log):
        """
        Evaluation on monolingual word similarity.
        """
        src_ws_scores = get_wordsim_scores(
            self.src_dico.lang, self.src_dico.word2id,
            self.mapping(self.src_emb.weight).data.cpu().numpy()
        )
        tgt_ws_scores = get_wordsim_scores(
            self.tgt_dico.lang, self.tgt_dico.word2id,
            self.tgt_emb.weight.data.cpu().numpy()
        ) if self.params.tgt_lang else None
        if src_ws_scores is not None:
            src_ws_monolingual_scores = np.mean(list(src_ws_scores.values()))
            logger.info("Monolingual source word similarity score average: %.5f" % src_ws_monolingual_scores)
            to_log['src_ws_monolingual_scores'] = src_ws_monolingual_scores
            to_log.update({'src_' + k: v for k, v in src_ws_scores.items()})
        if tgt_ws_scores is not None:
            tgt_ws_monolingual_scores = np.mean(list(tgt_ws_scores.values()))
            logger.info("Monolingual target word similarity score average: %.5f" % tgt_ws_monolingual_scores)
            to_log['tgt_ws_monolingual_scores'] = tgt_ws_monolingual_scores
            to_log.update({'tgt_' + k: v for k, v in tgt_ws_scores.items()})
        if src_ws_scores is not None and tgt_ws_scores is not None:
            ws_monolingual_scores = (src_ws_monolingual_scores + tgt_ws_monolingual_scores) / 2
            logger.info("Monolingual word similarity score average: %.5f" % ws_monolingual_scores)
            to_log['ws_monolingual_scores'] = ws_monolingual_scores

    def monolingual_wordanalogy(self, to_log):
        """
        Evaluation on monolingual word analogy.
        """
        src_analogy_scores = get_wordanalogy_scores(
            self.src_dico.lang, self.src_dico.word2id,
            self.mapping(self.src_emb.weight).data.cpu().numpy()
        )
        if self.params.tgt_lang:
            tgt_analogy_scores = get_wordanalogy_scores(
                self.tgt_dico.lang, self.tgt_dico.word2id,
                self.tgt_emb.weight.data.cpu().numpy()
            )
        if src_analogy_scores is not None:
            src_analogy_monolingual_scores = np.mean(list(src_analogy_scores.values()))
            logger.info("Monolingual source word analogy score average: %.5f" % src_analogy_monolingual_scores)
            to_log['src_analogy_monolingual_scores'] = src_analogy_monolingual_scores
            to_log.update({'src_' + k: v for k, v in src_analogy_scores.items()})
        if self.params.tgt_lang and tgt_analogy_scores is not None:
            tgt_analogy_monolingual_scores = np.mean(list(tgt_analogy_scores.values()))
            logger.info("Monolingual target word analogy score average: %.5f" % tgt_analogy_monolingual_scores)
            to_log['tgt_analogy_monolingual_scores'] = tgt_analogy_monolingual_scores
            to_log.update({'tgt_' + k: v for k, v in tgt_analogy_scores.items()})

    def crosslingual_wordsim(self, to_log):
        """
        Evaluation on cross-lingual word similarity.
        """
        src_emb = self.mapping(self.src_emb.weight).data.cpu().numpy()
        tgt_emb = self.tgt_emb.weight.data.cpu().numpy()
        # cross-lingual wordsim evaluation
        src_tgt_ws_scores = get_crosslingual_wordsim_scores(
            self.src_dico.lang, self.src_dico.word2id, src_emb,
            self.tgt_dico.lang, self.tgt_dico.word2id, tgt_emb,
        )
        if src_tgt_ws_scores is None:
            return
        ws_crosslingual_scores = np.mean(list(src_tgt_ws_scores.values()))
        logger.info("Cross-lingual word similarity score average: %.5f" % ws_crosslingual_scores)
        to_log['ws_crosslingual_scores'] = ws_crosslingual_scores
        to_log.update({'src_tgt_' + k: v for k, v in src_tgt_ws_scores.items()})


    def validate_words(self,to_log, src_words):
        # mapped word embeddings
        src_emb = self.mapping(self.src_emb.weight).data
        tgt_emb = self.tgt_emb.weight.data

        self.get_nn(src_words, src_emb, self.src_dico.id2word, tgt_emb, self.tgt_dico.id2word, 10, to_log)


    def new_translation(self, to_log):
        """
        Evaluation on word translation.
        """
        # mapped word embeddings
        src_emb = self.mapping(self.src_emb.weight).data
        tgt_emb = self.tgt_emb.weight.data





        src_words = [u'og', 'ikki', 'ja', 'at', 'hvussu', 'morgin' , 'gud', u'eta']
        # src_words = ['und', 'nicht', 'ja', 'zu', 'wie', 'morgen', 'gott', 'essen']


        self.get_nn(src_words, src_emb, self.src_dico.id2word, tgt_emb, self.tgt_dico.id2word, 10, to_log)

    def get_nn(self, words, src_emb, src_id2word, tgt_emb, tgt_id2word, K, to_log):
        total_scores = []
        all_words = []
        word_dict = {}



        for word in words:
            word_dict[word] = []
            word_score_list = word + ":"
            # print("Nearest neighbors of \"%s\":" % word)
            word2id = {v: k for k, v in src_id2word.items()}
            if word.decode('utf8') in word2id.keys():
                print word.decode('utf8')
                word_emb = src_emb[word2id[word.decode("utf8")]].cpu().numpy()
                scores = (tgt_emb.cpu().numpy() / np.linalg.norm(tgt_emb.cpu().numpy(), 2, 1)[:, None]).dot(word_emb / np.linalg.norm(word_emb))

                k_best = scores.argsort()[-K:][::-1]
                best_scores = []
                for i, idx in enumerate(k_best):
                    # print('%.4f - %s' % (scores[idx], tgt_id2word[idx]))
                    # word_score_list  += "\n " + str(scores[idx]) + " - " + tgt_id2word[idx].decode("utf8")
                    word_dict[word].append(tgt_id2word[idx])
                    best_scores.append(scores[idx])
                all_words.append(word_score_list)
                total_scores.append(np.mean(best_scores))
        to_log["Words"] = all_words
        to_log["Word_Scores"] = np.mean(total_scores)
        to_log["Word_dict"] = word_dict


    def word_translation(self, to_log):
        """
        Evaluation on word translation.
        """
        # mapped word embeddings
        src_emb = self.mapping(self.src_emb.weight).data
        tgt_emb = self.tgt_emb.weight.data

        for method in ['nn', 'csls_knn_10']:
            results = get_word_translation_accuracy(
                self.src_dico.lang, self.src_dico.word2id, src_emb,
                self.tgt_dico.lang, self.tgt_dico.word2id, tgt_emb,
                method=method,
                dico_eval=self.params.dico_eval
            )
            to_log.update([('%s-%s' % (k, method), v) for k, v in results])

    def sent_translation(self, to_log):
        """
        Evaluation on sentence translation.
        Only available on Europarl, for en - {de, es, fr, it} language pairs.
        """
        lg1 = self.src_dico.lang
        lg2 = self.tgt_dico.lang

        # parameters
        n_keys = 200000
        n_queries = 2000
        n_idf = 300000

        # load europarl data
        if not hasattr(self, 'europarl_data'):
            self.europarl_data = load_europarl_data(
                lg1, lg2, n_max=(n_keys + 2 * n_idf)
            )

        # if no Europarl data for this language pair
        if not self.europarl_data:
            return

        # mapped word embeddings
        src_emb = self.mapping(self.src_emb.weight).data
        tgt_emb = self.tgt_emb.weight.data

        # get idf weights
        idf = get_idf(self.europarl_data, lg1, lg2, n_idf=n_idf)

        for method in ['nn', 'csls_knn_10']:

            # source <- target sentence translation
            results = get_sent_translation_accuracy(
                self.europarl_data,
                self.src_dico.lang, self.src_dico.word2id, src_emb,
                self.tgt_dico.lang, self.tgt_dico.word2id, tgt_emb,
                n_keys=n_keys, n_queries=n_queries,
                method=method, idf=idf
            )
            to_log.update([('tgt_to_src_%s-%s' % (k, method), v) for k, v in results])

            # target <- source sentence translation
            results = get_sent_translation_accuracy(
                self.europarl_data,
                self.tgt_dico.lang, self.tgt_dico.word2id, tgt_emb,
                self.src_dico.lang, self.src_dico.word2id, src_emb,
                n_keys=n_keys, n_queries=n_queries,
                method=method, idf=idf
            )
            to_log.update([('src_to_tgt_%s-%s' % (k, method), v) for k, v in results])

    def dist_mean_cosine(self, to_log):
        """
        Mean-cosine model selection criterion.
        """
        # get normalized embeddings
        src_emb = self.mapping(self.src_emb.weight).data
        tgt_emb = self.tgt_emb.weight.data
        src_emb = src_emb / src_emb.norm(2, 1, keepdim=True).expand_as(src_emb)
        tgt_emb = tgt_emb / tgt_emb.norm(2, 1, keepdim=True).expand_as(tgt_emb)

        # build dictionary
        for dico_method in ['nn', 'csls_knn_10']:
            dico_build = 'S2T'
            dico_max_size = 10000
            # temp params / dictionary generation
            _params = deepcopy(self.params)
            _params.dico_method = dico_method
            _params.dico_build = dico_build
            _params.dico_threshold = 0
            _params.dico_max_rank = 10000
            _params.dico_min_size = 0
            _params.dico_max_size = dico_max_size
            s2t_candidates = get_candidates(src_emb, tgt_emb, _params)
            t2s_candidates = get_candidates(tgt_emb, src_emb, _params)
            dico = build_dictionary(src_emb, tgt_emb, _params, s2t_candidates, t2s_candidates)
            # mean cosine
            if dico is None:
                mean_cosine = -1e9
            else:
                mean_cosine = (src_emb[dico[:dico_max_size, 0]] * tgt_emb[dico[:dico_max_size, 1]]).sum(1).mean()
            mean_cosine = mean_cosine.item() if isinstance(mean_cosine, torch_tensor) else mean_cosine
            logger.info("Mean cosine (%s method, %s build, %i max size): %.5f"
                        % (dico_method, _params.dico_build, dico_max_size, mean_cosine))
            to_log['mean_cosine-%s-%s-%i' % (dico_method, _params.dico_build, dico_max_size)] = mean_cosine

            # Used for tensorboardX
            if dico_method == 'nn':
                to_log['mean_nn'] = mean_cosine
            else:
                to_log['mean_csls'] = mean_cosine



    def all_eval(self, to_log):
        """
        Run all evaluations.
        """
        # self.monolingual_wordsim(to_log)
        # self.crosslingual_wordsim(to_log)
        # self.new_translation(to_log)
        # self.sent_translation(to_log)
        self.dist_mean_cosine(to_log)

    def eval_dis(self, to_log):
        """
        Evaluate discriminator predictions and accuracy.
        """
        bs = 128
        src_preds = []
        tgt_preds = []

        self.discriminator.eval()

        for i in range(0, self.src_emb.num_embeddings, bs):
            emb = Variable(self.src_emb.weight[i:i + bs].data, requires_grad=True)
            preds = self.discriminator(self.mapping(emb))
            src_preds.extend(preds.data.cpu().tolist())

        for i in range(0, self.tgt_emb.num_embeddings, bs):
            emb = Variable(self.tgt_emb.weight[i:i + bs].data, requires_grad=True)
            preds = self.discriminator(emb)
            tgt_preds.extend(preds.data.cpu().tolist())

        src_pred = np.mean(src_preds)
        tgt_pred = np.mean(tgt_preds)
        logger.info("Discriminator source / target predictions: %.5f / %.5f"
                    % (src_pred, tgt_pred))

        src_accu = np.mean([x >= 0.5 for x in src_preds])
        tgt_accu = np.mean([x < 0.5 for x in tgt_preds])
        dis_accu = ((src_accu * self.src_emb.num_embeddings + tgt_accu * self.tgt_emb.num_embeddings) /
                    (self.src_emb.num_embeddings + self.tgt_emb.num_embeddings))
        logger.info("Discriminator source / target / global accuracy: %.5f / %.5f / %.5f"
                    % (src_accu, tgt_accu, dis_accu))

        to_log['src_accu'] = src_accu
        to_log['tgt_accu'] = tgt_accu
        to_log['dis_accu'] = dis_accu
        to_log['dis_src_pred'] = src_pred
        to_log['dis_tgt_pred'] = tgt_pred
