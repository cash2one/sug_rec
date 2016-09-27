#!/usr/bin/python
# coding:utf-8
#coding:utf-8
#-------------------------------------------------------------------------------
# Name: sug_similarity
# Purpose:计算新闻sug之间的相似度
# Author:yinke
#-------------------------------------------------------------------------------
import os
import time
import re
import jieba.analyse
import jieba
from gensim import corpora, models, similarities
import os
import random
from pprint import pprint
import collections
import logging
from collections import defaultdict
from pprint import pprint  # pretty-printer
import sys
import chardet
from query_addition_sug import get_query_addition
from xrank_analyze import parseJson,parseJsonbyid,parseJson2dict
import myssh
import argparse

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

XRANK_DIR = '/home/work/yinke/xrank_opt'

class GetRawCorpus(object):
    def __init__(self,args):
        self.texts = []
        self.args = args
    def __iter__(self):
        addition_file = open('addition_file.txt','w')
        for text in parseJson('xrank.json'):
        # for text in open('addition_file.txt','r'):
            term = text.strip()
            print term
            if  self.args.addition:
                item = get_query_addition(term)
                if len(item) < 1:
                    item = term
            else:
                item = term
            item = item.strip()
            addition_file.write(item + '\n')
            seg_list = jieba.lcut_for_search(item)  # get keywords
            # print ' '.join(seg_list)
            yield seg_list

    def remove_once_words(self):

        frequency = defaultdict(int)
        for text in GetRawCorpus(self.args):
            for token in text:
                frequency[token] += 1
        self.texts = [[token for token in text if frequency[token] >= 1] for text in GetRawCorpus(self.args)]
        # print len(self.texts)
        # for text in self.texts:
        #     for word in text:
        #         print word




    def remove_stop_words(self):    #从stoplist_cn里读取停用词，然后解决混合编码的问题，统一编码成utf8
        stoplist_mix_encode = set()
        stoplist = set()
        for line in open('/home/work/yinke/xrank_opt/calcu_sug_sim/stoplist_cn.txt'):
            stoplist_mix_encode.add(line.strip())
        stoplist_mix_encode.remove('')
        self.texts = [[word.encode('utf-8') for word in text if word.encode('utf8') not in stoplist_mix_encode]
                      for text in self.texts]
        print len(self.texts)
        # for text in self.texts:
        #     print ''.join(text)



class Trans2tfidf(GetRawCorpus):
    def __init__(self):
        self.corpus_bow = []
    def trans2dict(self):
        # for text in self.texts:
        #     print ' '.join(text)
        if os.path.exists(os.path.join(XRANK_DIR + '/sougou_train/model_trained', 'sougou_news.dict')):
            print 'find sougou_news.dict'
            self.dictionary  = corpora.Dictionary.load(os.path.join(XRANK_DIR + '/sougou_train/model_trained', 'sougou_news.dict'))
        else:
            self.dictionary = corpora.Dictionary(self.texts)
        # for key,value in self.dictionary.token2id.iteritems():
        #     print key,value
        self.corpus_bow = [self.dictionary.doc2bow(text) for text in self.texts]
        # print self.corpus_bow

    def trans2tfidf(self):
        if os.path.exists(os.path.join(XRANK_DIR + '/sougou_train/model_trained', 'model.tfidf')):
            print 'find model.tfidf'
            self.tfidf = models.TfidfModel.load('/home/work/yinke/xrank_opt/sougou_train/model_trained/model.tfidf')
        else:
            self.tfidf = models.TfidfModel(self.corpus_bow)

        self.corpus_tfidf = self.tfidf[self.corpus_bow]
        self.corpus_tfidf.save(os.path.join(XRANK_DIR + '/sug_cluster', 'corpus.tfidf'))


class Trans2TopicModel(Trans2tfidf):
    def __init__(self):
        self.corpus_lsi = []

    def trans2lsi(self):
        if os.path.exists(os.path.join(XRANK_DIR + '/sougou_train/model_trained', 'model.lsi')):
            print( 'find model.lsi')
            self.lsi = models.LsiModel.load(os.path.join(XRANK_DIR + '/sougou_train/model_trained', 'model.lsi'))
            self.corpus_lsi = self.lsi[self.corpus_tfidf]
        else:
            self.lsi = models.LsiModel(self.corpus_tfidf, id2word=self.dictionary, num_topics=40)  # 初始化一个LSI转换

        self.corpus_lsi = self.lsi[self.corpus_tfidf]

        self.corpus_lsi.save(os.path.join(XRANK_DIR + '/sug_cluster', 'corpus.lsi'))


    def trans2lda(self):

        # self.lda = models.LdaModel.load('/home/work/yinke/xrank_opt/sougou_train/model_trained/model.lda')
        if os.path.exists(os.path.join(XRANK_DIR + '/sougou_train/model_trained', 'model.lda')):
            print( 'find model.lda')
            self.lda = models.LsiModel.load(os.path.join(XRANK_DIR + '/sougou_train/model_trained', 'model.lda'))
            self.corpus_lda = self.lda[self.corpus_tfidf]
        else:
            self.lda = models.LsiModel(self.corpus_tfidf, id2word=self.dictionary, num_topics=40)  # 初始化一个LSI转换

        self.corpus_lda = self.lda[self.corpus_tfidf]

        self.corpus_lda.save(os.path.join(XRANK_DIR + '/sug_cluster', 'corpus.lda'))




class CalculateSimilarity(Trans2TopicModel):
    def __init__(self,args):
        self.corpus_sim = []
        self.args = args

    def calcu_sim(self):
        index_lsi = similarities.MatrixSimilarity(self.corpus_lsi)
        index_lsi.save(os.path.join(XRANK_DIR + '/sim_result_index', 'index.lsi'))


    def calcu_simMatrixbyid_lsi(self):          #计算相似度矩阵，利用新闻的id
        # index_lda = similarities.MatrixSimilarity(self.corpus_lda)
        index_lsi = similarities.MatrixSimilarity(self.corpus_lsi)
        index_lsi.save(os.path.join('/home/work/yinke/yrank_rec/index','index.lsi'))
        id_list = parseJsonbyid('xrank.json')
        text_list = parseJson('xrank.json')
        sim_result = open('text_similarity.txt','w')
        for  i in range(len(self.corpus_lsi)):
            sim_lsi = index_lsi[self.corpus_lsi[i]]
            sims = sorted(enumerate(sim_lsi), key=lambda item: -item[1])
            line = ''
            text_line = ''
            for set in sims :
                if set[1] > 0.5:
                    line =  line + str(id_list[set[0]]) + ':' + str(set[1]) + ','
                    text_line =  text_line + str(text_list[set[0]]) + ':' + str(set[1]) + ','
                else:
                    break
            line = line.strip(',') + '\n'
            text_line = text_line.strip(',') + '\n'
            print text_line
            sim_result.write(line)
    def calcu_simMatrixbyid_lda(self):          #计算相似度矩阵，利用新闻的id
        index_lda = similarities.MatrixSimilarity(self.corpus_lda)
        # index_lsi = similarities.MatrixSimilarity(self.corpus_lsi)
        id_list = parseJsonbyid('xrank.json')
        text_list = parseJson('xrank.json')
        sim_result = open('text_similarity.txt','w')
        for  i in range(len(self.corpus_lda)):
            sim_lda = index_lda[self.corpus_lda[i]]
            sims = sorted(enumerate(sim_lda), key=lambda item: -item[1])
            line = ''
            text_line = ''
            for set in sims :
                if set[1] > 0.707:
                    line =  line + str(id_list[set[0]]) + ':' + str(set[1]) + ','
                    text_line =  text_line + str(text_list[set[0]]) + ':' + str(set[1]) + ','
                else:
                    break
            line = line.strip(',') + '\n'
            text_line = text_line.strip(',') + '\n'
            print text_line
            sim_result.write(line)




if __name__ == '__main__':

    ######从sj02拉数据过来
    remote_host = 'cq02-sw-sj00.cq02.baidu.com'
    remote_file_pulled = '/home/work/publish/project/medusa_xrank_score/outputs/xrank.json'
    local_file = '/home/work/yinke/xrank_opt/sug_sim_addition/xrank.json'
    sshOperator = myssh.SSHClientCache(user= 'work',passwd='xf_server@baidu')
    sshOperator.pull_remote_file_to_local(remote_host, remote_file_pulled, local_file)


    ###定义参数
    parser = argparse.ArgumentParser()
    parser.add_argument("-model",type=str,required=True,help="选择模型：'lda'or'lsi'")
    parser.add_argument('-addition',type = int,required = True,help = "是否进行文本扩充" )
    args = parser.parse_args(sys.argv[1:])

    #计算相似度
    tic = time.clock()
    topic_model = CalculateSimilarity(args)
    topic_model.remove_once_words()
    toc = time.clock()
    print toc
    topic_model.remove_stop_words()
    topic_model.trans2dict()
    topic_model.trans2tfidf()
    if args.model == 'lsi':
        topic_model.trans2lsi()
        topic_model.calcu_simMatrixbyid_lsi()
    elif args.model == 'lda':
        topic_model.trans2lda()
        topic_model.calcu_simMatrixbyid_lda()
    else:
        parser.print_help()

    toc = time.clock()
    print "it takes about ",toc

    # 传给 yq01-sw-hdsserver00.yq01.baidu.com
    remote_host2 = 'yq01-sw-hdsserver00.yq01.baidu.com'
    remote_file_pushed = '/home/sw_sj_sh/publish/medusa_xrank_project/medusa_xrank_score/outputs/xrank_with_similarity/text_similarity.txt'
    local_file = '/home/work/yinke/xrank_opt/sug_sim_addition/text_similarity.txt'
    sshOperator = myssh.SSHClientCache(user= 'sw_sj_sh',passwd='sw_sj_sh@baidu')
    sshOperator.push_local_file_to_remote(remote_host2, remote_file_pushed, local_file)


