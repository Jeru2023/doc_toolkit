from scipy.cluster.hierarchy import ward
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import jieba.posseg
import re
from tools.utils import timer


class TopicCluster:

    @staticmethod
    def tokenizer(doc):
        text = re.sub('\W*', '', ''.join(doc))
        words = jieba.posseg.cut(text)

        POS = ('n', 'nz', 'ns', 'nt', 'nr', 'l')
        blacklist = ['公司', '企业', '行业', '产品', '核心', '报告', '事项', '平台', '子公司', '性', '项', '实际',
                     '情况', '年度']

        pos_words = []
        for word, flag in words:
            if (flag in POS) and (word not in blacklist):
                pos_words.append(word)

        return pos_words

    def get_tfidf_matrix(self, docs):
        tokenizer = self.tokenizer(docs)
        # chosen n-gram of three words. It will produce phrases containing upto three words
        vectorizer = TfidfVectorizer(min_df=5, stop_words='english', tokenizer=self.tokenizer, ngram_range=(1, 3))

        # fit the vectorizer to documents
        tfidf_matrix = vectorizer.fit_transform(docs)

        return tfidf_matrix

    @timer
    def cluster(self, docs):
        tfidf_matrix = self.get_tfidf_matrix(docs)

        # using cosine distance
        dist = 1 - cosine_similarity(tfidf_matrix)
        linkage_matrix = ward(dist)

        return linkage_matrix

