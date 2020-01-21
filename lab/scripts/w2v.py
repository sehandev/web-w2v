# -*- coding: utf-8 -*- 

from sshtunnel import SSHTunnelForwarder
import pymongo
import datetime
import random
import time
import re

from gensim.models.callbacks import CallbackAny2Vec
from gensim.models.word2vec import Word2Vec
from gensim.scripts.word2vec2tensor import word2vec2tensor
from gensim import utils
from konlpy.tag import Mecab

from .visualization import visualize


# static variables
DATA_DIR = '/searchpert-w2v/lab/scripts/data/'

# 보안을 위해 DB서버 정보를 따로 보관
with open(DATA_DIR + 'connection.txt', 'r') as file:
    connection_data = file.read().split()
MONGO_HOST = (connection_data[0], int(connection_data[1]))  # host server addr, port
MONGO_USER = connection_data[2]  # ssh username
MONGO_PASS = connection_data[3]  # ssh password
MONGO_DB = 'spert_crawler'
MONGO_COLLECTION = 'final_nogitrmal'
QUERY_LIMIT = 20


class callback(CallbackAny2Vec):
    # Mecab 학습 callback -> epoch와 loss 출력

    def __init__(self):
        self.epoch = 1
        self.start_time = time.time()

    def on_epoch_end(self, model):
        loss = model.get_latest_training_loss()

        finish_time = int(time.time() - self.start_time)
        print('Loss after epoch {}: {}'.format(self.epoch, loss), end='\t')
        print("{}:{}".format(finish_time // 60, finish_time % 60))

        self.epoch += 1


class Searchpert_w2v:
    def __init__(self, term_count):
        self.term_count = term_count

        self.mecab = Mecab()
        self.term_sentences = []  # 기간에 따른 data list
        self.term_models = []  # 기간에 따른 mecab model list
        self.term_words = []  # 기간에 따른 word list

        # 기준에 따라 나눈 날짜 (16대 노무현, 17대 이명박, 18대 박근혜, 19대 문재인)
        self.from_date = [
            datetime.datetime(2017, 5, 1),
            datetime.datetime(2013, 3, 1),
            datetime.datetime(2008, 3, 1),
            datetime.datetime(2003, 3, 1)
            ]
        self.to_date = [
            datetime.datetime(2019, 10, 31, 23, 59, 59, 000000),
            datetime.datetime(2015, 8, 31, 23, 59, 59, 000000),
            datetime.datetime(2010, 8, 31, 23, 59, 59, 000000),
            datetime.datetime(2005, 8, 31, 23, 59, 59, 000000)
            ]

        self.term_name = ['문재인', '박근혜', '이명박', '노무현']

        # self.load_sentences_from_db()
        self.load_sentences_from_file()
        self.build_model()
        # self.load_model()


    def load_sentences_from_db(self):
        # DB로부터 data 받아와서 전처리 거치기 (+ file에 저장)

        print('\nStart : load from DB')
        start_time = time.time()

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
        
        for i in range(self.term_count):

            # 기간에 해당하는 data만 읽기 (+ 테스트를 위해 limit 추가)
            cursor = collection.find(
                {
                    'date': {'$gte': self.from_date[i], '$lt': self.to_date[i]},
                    'tag': {'$or' : ['감사원', '경찰청', '고용노동부', '공정거래위원회', '과학기술정보통신부', '관세청', '교육부', '국가보훈처', '국가인권위원회', '국가정보원 국무조정실', '국민권익위원회', '국방부', '국세청', '국토교통부', '금융위원회', '기상청', '기획재정부', '농림축산식품부', '농촌진흥청', '대검찰청', '대통령경호처', '전자관보', '문화재청', '문화체육관광부', '방송통신위원회', '방위사업청', '법무부', '법제처', '병무청', '보건복지부', '산림청', '산업통상자원부', '새만금개발청', '식품의약품안전처', '여성가족부', '외교부', '원자력안전위원회', '인사혁신처', '정부24', '정책브리핑', '조달청', '중소벤처기업부', '통계청', '통일부', '특허청', '해양수산부', '행정안전부', '행정중심복합도시건설청', '환경부']},
                }
                # ,limit=QUERY_LIMIT
                )

            # DB에서 cursor로 data 읽기
            sentences = []
            for document in cursor:
                tmp = document['content'].strip()  # 내용만 읽어오기
                if tmp:  # 내용이 있다면
                    sentences.append(tmp)
            
            # 전처리 (preprocessing)
            sentences = self.remove_irregular(sentences)  # 한글, 영어만 남기기
            sentences = self.mecab_processing(sentences)  # mecab 형태소분석

            self.term_sentences.append(sentences)

            # 시간 단축을 위해 file에 저장
            with open(DATA_DIR + 'center_data_{}.txt'.format(i), 'w') as file:
                for sentence in self.term_sentences[i]:
                    file.write(' '.join(sentence) + '\n')

            finish_time = int(time.time() - start_time)
            print('Finish : load sentences from DB - {}'.format(i), end='\t')
            print('{}:{}'.format(finish_time // 60, finish_time % 60))

        server.stop()  # ssh tunnel close


    def load_sentences_from_file(self):
        # file에서 data 받기
        
        print('\nStart : load from file')
        start_time = time.time()
        for i in range(self.term_count):
            with open(DATA_DIR + 'train/' + 'sehan_data_test_' + self.term_name[i] + '.txt', 'r', errors='ignore') as infile:
                sentences = []
                for cnt, line in enumerate(infile):
                    sentences.append(line.split())
                    if cnt % 100000 == 0:
                        print(cnt)

                self.term_sentences.append(sentences)

            finish_time = int(time.time() - start_time)
            print("Finish : load sentences from file - {}".format(i), end='\t')
            print("{}:{}".format(finish_time // 60, finish_time % 60))


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

        for i in range(self.term_count):
            model = Word2Vec.load(DATA_DIR + 'model/' + 'wv_' + self.term_name[i] + '.model')
            self.term_models.append(model)
            
            w2c = dict()
            for item in model.wv.vocab:
                w2c[item]=model.wv.vocab[item].count
            self.term_words.append(dict(sorted(w2c.items(), key=lambda x: x[1],reverse=True)))
            
            model.wv.save_word2vec_format(DATA_DIR + 'tf_vector/' + 'wv_format_' + self.term_name[i] + '.bin', binary=True)  # word2vec2tensor를 위한 저장
            model.init_sims(replace=True)  # word2vec의 불필요한 memory unload

            finish_time = int(time.time() - start_time)
            print("Finish : load word2vec model - {}".format(i), end='\t')
            print("{}:{}".format(finish_time // 60, finish_time % 60))

        self.vector_to_tsv()
        for i in range(self.term_count):
            visualize(model, DATA_DIR, i)  # 시각화

            finish_time = int(time.time() - start_time)
            print("Finish : load word2vec model - {}".format(i), end='\t')
            print("{}:{}".format(finish_time // 60, finish_time % 60))


    def build_model(self):
        # word2vec 학습하기 

        start_time = time.time()
        print('\nStart : word2vec model')

        for i in range(1, self.term_count):
            tmp_sentences = self.term_sentences[i]
            random.shuffle(tmp_sentences)  # randomly shuffled list

            # word2vec : sg(CBOW, Skip-gram), sentences(학습할 문장), size(vector 차원 크기), window(주변 단어), min_count(최소 단어 개수)
            model = Word2Vec(sg=1, sentences=tmp_sentences, size=256, window=5, min_count=10, workers=40, iter=10, compute_loss=True, callbacks=[callback()])
            model.save(DATA_DIR + 'model/' + 'wv_' + self.term_name[i] + '.model')  # model 저장
            model.wv.save_word2vec_format(DATA_DIR + 'tf_vector/' + 'wv_format_' + self.term_name[i] + '.bin', binary=True)  # word2vec2tensor를 위한 저장
            self.term_models.append(model)

            model.init_sims(replace=True)  # word2vec의 불필요한 memory unload

            finish_time = int(time.time() - start_time)
            print("Finish : build word2vec model - {}".format(i), end='\t')
            print("{}:{}".format(finish_time // 60, finish_time % 60))

        self.vector_to_tsv()
        for i in range(self.term_count):
            visualize(model, DATA_DIR, i)  # 시각화

            finish_time = int(time.time() - start_time)
            print("Finish : load word2vec model - {}".format(i), end='\t')
            print("{}:{}".format(finish_time // 60, finish_time % 60))


    def vector_to_tsv(self):
        start_time = time.time()
        print('\nStart : w2v to tensor')

        for i in range(self.term_count):
            model_path = DATA_DIR + 'tf_vector/' + 'wv_format_' + self.term_name[i] + '.bin'
            tensor_tsv_name = DATA_DIR + 'tsv/' + 'wv_' + self.term_name[i]
            word2vec2tensor(model_path, tensor_tsv_name, binary=True)

            finish_time = int(time.time() - start_time)
            print("Finish : w2v to tensor - {}".format(i), end='\t')
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


searchpert_w2v = Searchpert_w2v(2)  # instance create

# if __name__ == '__main__':
#     # Test
#     print(searchpert_w2v.most_similar('조례', 1))  # 테스트
