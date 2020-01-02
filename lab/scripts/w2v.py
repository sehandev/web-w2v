# -*- coding: utf-8 -*- 

from sshtunnel import SSHTunnelForwarder
import pymongo

from gensim.test.utils import common_texts, get_tmpfile
from gensim.models.callbacks import CallbackAny2Vec
from gensim.models.word2vec import Word2Vec
from gensim.scripts.word2vec2tensor import word2vec2tensor
from gensim import utils
from konlpy.tag import Mecab

import datetime
import random
import time
import re


# static variables
DATA_DIR = '/searchpert-w2v/lab/scripts/data/'
TERM_COUNT = 4

# 보안을 위해 DB서버 정보를 따로 보관
with open(DATA_DIR + 'connection.txt', 'r') as file:
    connection_data = file.read().split()
MONGO_HOST = (connection_data[0], int(connection_data[1]))  # host server addr, port
MONGO_USER = connection_data[2]  # ssh username
MONGO_PASS = connection_data[3]  # ssh password
MONGO_DB = 'spert_crawler'
MONGO_COLLECTION = 'final_normal'
QUERY_LIMIT = 200000


class callback(CallbackAny2Vec):
    # Mecab 학습 callback -> epoch와 loss 출력

    def __init__(self):
        self.epoch = 1

    def on_epoch_end(self, model):
        loss = model.get_latest_training_loss()
        print('Loss after epoch {}: {}'.format(self.epoch, loss))
        self.epoch += 1


class Searchpert_w2v:
    def __init__(self):
        self.TERM_COUNT = 4

        self.mecab = Mecab()
        self.term_sentences = []  # 기간에 따른 data list
        self.term_models = []  # 기간에 따른 mecab model list
        self.term_words = []  # 기간에 따른 word list

        self.load_sentences_from_db()
        # self.load_sentences_from_file()
        self.build_model()

        # self.load_model()

        # self.vector_to_tsv()


    def load_sentences_from_db(self):
        # DB로부터 data 받아와서 전처리 거치기 (+ file에 저장)
        print('\nStart : load from DB')

        # 원격 접속을 위한 ssh tunnel
        server = SSHTunnelForwarder(
            MONGO_HOST,
            ssh_username=MONGO_USER,
            ssh_password=MONGO_PASS,
            remote_bind_address=('127.0.0.1', 27017)
        )
        server.daemon_forward_servers = True  # python3.7에서 server.stop()이 진행되지 않은 bug를 해결하기 위한 편법

        server.start()  # ssh tunnel open

        # local mongoDB 접속
        client = pymongo.MongoClient('127.0.0.1', server.local_bind_port)  # local_bind_port : sshTunnel을 통해 원격 mongoDB에 접속된 port
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION]

        # 기준에 따라 나눈 날짜 (16대 노무현, 17대 이명박, 18대 박근혜, 19대 문재인)
        from_date = [
            datetime.datetime(2003, 3, 1),
            datetime.datetime(2008, 3, 1),
            datetime.datetime(2013, 3, 1),
            datetime.datetime(2017, 5, 1)
            ]
        to_date = [
            datetime.datetime(2005, 8, 31, 23, 59, 59, 000000),
            datetime.datetime(2010, 8, 31, 23, 59, 59, 000000),
            datetime.datetime(2015, 8, 31, 23, 59, 59, 000000),
            datetime.datetime(2019, 10, 31, 23, 59, 59, 000000)
            ]
        
        for i in range(TERM_COUNT):

            # 기간에 해당하는 data만 읽기 (+ 테스트를 위해 limit 추가)
            cursor = collection.find(
                {"date": {'$gte': from_date[i], '$lt': to_date[i]}}
                # ,limit=QUERY_LIMIT
                )

            # DB에서 cursor로 data 읽기
            sentences = []
            for document in cursor:
                if document['content'].strip():
                    sentences.append(document['content'])
            
            # 전처리 (preprocessing)
            sentences = self.remove_irregular(sentences)  # 한글, 영어만 남기기
            sentences = self.mecab_processing(sentences)  # mecab 형태소분석

            self.term_sentences.append(sentences)
            print("Finish : load sentences from DB - {}".format(i))

        server.stop()  # ssh tunnel close

        # 시간 단축을 위해 file에 저장
        for i in range(TERM_COUNT):
            with open(DATA_DIR + 'center_data_' + str(i) + '.txt', 'w') as file:
                for sentence in self.term_sentences[i]:
                    file.write(' '.join(sentence) + '\n')

        print("Finish : write in file")


    def load_sentences_from_file(self):
        # file에서 data 받기
        
        print('\nStart : load from file')
        start_time = time.time()
        for i in range(TERM_COUNT):
            with open(DATA_DIR + 'center_data_' + str(i) + '.txt', 'r') as infile:

                sentences = []
                for cnt, line in enumerate(infile):
                    sentences.append(line.split())
                    if cnt % 100000 == 0:
                        print(cnt)

                self.term_sentences.append(sentences)

        finish_time = int(time.time() - start_time)
        print("{}:{}".format(finish_time // 60, finish_time % 60))
        print("Finish : load sentences from file")


    def remove_irregular(self, sentences):
        # 한글, 영어만 남기기

        regular = re.compile('[가-힣a-zA-Z]+')

        new_sentences = []
        for sentence in sentences:
            regular_words = regular.findall(sentence)
            new_sentences.append(' '.join(regular_words))

        return new_sentences
            

    def mecab_processing(self, sentences):
        # Mecab을 이용해서 문장을 형태소로 분석
        
        after_process = []
        for sentence in sentences:
            result_mecab = self.mecab.morphs(sentence)  # 형태소 분석
            after_process.append(result_mecab)

        return after_process


    def load_model(self):
        # word2vec load하기 

        start_time = time.time()
        print('\nStart : word2vec model')

        for i in range(TERM_COUNT):
            model = Word2Vec.load(DATA_DIR + 'wv_' + str(i) + '.model')
            self.term_models[i].append(model)
            
            w2c = dict()
            for item in model.wv.vocab:
                w2c[item]=model.wv.vocab[item].count
            self.term_words.append(dict(sorted(w2c.items(), key=lambda x: x[1],reverse=True)))
            
            model.wv.save_word2vec_format(DATA_DIR + 'wv_format_' + str(i) + '.wv', binary=True)  # word2vec2tensor를 위한 저장

            model.init_sims(replace=True)  # word2vec의 불필요한 memory unload

            print("Finish : load word2vec model - {}".format(i))

        finish_time = int(time.time() - start_time)
        print("{}:{}".format(finish_time // 60, finish_time % 60))


    def build_model(self):
        # word2vec 학습하기 

        start_time = time.time()
        print('\nStart : word2vec model')

        for i in range(TERM_COUNT):
            tmp_sentences = self.term_sentences[i]
            random.shuffle(tmp_sentences)  # randomly shuffled list
            model = Word2Vec(sentences=tmp_sentences, size=256, window=5, min_count=10, workers=2, iter=50, compute_loss=True, callbacks=[callback()])
            model.save(DATA_DIR + 'wv_' + str(i) + '.model')  # model 저장
            model.wv.save_word2vec_format(DATA_DIR + 'wv_format_' + str(i) + '.wv')  # word2vec2tensor를 위한 저장
            self.term_models[i].append(model)

            model.init_sims(replace=True)  # word2vec의 불필요한 memory unload

            print("Finish : build word2vec model - {}".format(i))

        finish_time = int(time.time() - start_time)
        print("{}:{}".format(finish_time // 60, finish_time % 60))


    def vector_to_tsv(self):
        start_time = time.time()
        print('\nStart : w2v to tensor')

        for i in range(TERM_COUNT):
            model_path = DATA_DIR + 'wv_format_' + str(i) + '.wv'
            tensor_tsv_name = DATA_DIR + 'wv_' + str(i)
            word2vec2tensor(model_path, tensor_tsv_name, binary=True)
            print("Finish : w2v to tensor - {}".format(i))

        finish_time = int(time.time() - start_time)
        print("{}:{}".format(finish_time // 60, finish_time % 60))


    def most_similar(self, search_word, term=1, topn=10):
        # search_word와 가장 비슷한 단어 topn개

        if search_word == '':
            # 입력한 단어 없이 검색
            return -1, 0, 0

        try:
            # 입력한 단어가 vector로 있으면
            most_similar_word = self.term_models[term].wv.most_similar(search_word, topn=topn)  # 가장 비슷한 단어

            similar_count = []
            for similar_word, _ in most_similar_word:
                similar_count.append(self.term_words[term][similar_word])
            return most_similar_word, similar_count, self.term_words[term][search_word]
        except:
            # 입력한 단어가 없으면
            return -1, 0, 0


searchpert_w2v = Searchpert_w2v()  # instance create

# if __name__ == '__main__':
#     # Test
#     print(searchpert_w2v.most_similar('조례', 1))  # 테스트
