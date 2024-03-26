# coding=utf-8
from gensim.models import Word2Vec
from gensim.models import KeyedVectors

model = KeyedVectors.load('../models/word2vec/tencent-ailab-embedding-zh-d200-v0.2.0-s.bin')   #用模型
#model = KeyedVectors.load_word2vec_format('../models/word2vec/tencent-ailab-embedding-zh-d200-v0.2.0-s.txt')  # 用转换成txt的词向量文件
#model.save('../models/word2vec/tencent-ailab-embedding-zh-d200-v0.2.0-s.bin')
testwords = ['新冠', '宁德时代', '喜茶', '海底捞', '罗胖', '刘德华', '医美', '盲盒', '共享经济', '发展趋势']
for i in range(10):
    res = model.most_similar(testwords[i])
    print(testwords[i])
    print(res)
