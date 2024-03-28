import jieba
import jieba.posseg
import re

POS = ('n', 'nz', 'ns', 'nt', 'nr', 'l')


class WordCutter:
    @staticmethod
    def cut(text):
        text = re.sub('\W*', '', ''.join(text))
        words = jieba.posseg.cut(text)

        blacklist = ['公司', '企业', '行业', '产品', '核心', '报告', '事项', '平台', '子公司', '性', '项', '实际',
                     '情况', '年度']

        pos_words = []
        for word, flag in words:
            if (flag in POS) and (word not in blacklist):
                pos_words.append(word)

        return pos_words
