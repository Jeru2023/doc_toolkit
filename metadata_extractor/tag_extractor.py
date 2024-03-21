import jieba.analyse
from tools import utils
import os

#POS = ('n', 'nz', 'v', 'vd', 'vn', 'l', 'a', 'd')
POS = ('n', 'nz', 'ns', 'nt', 'nr', 'l')


class TagExtractor:
    def __init__(self):
        self.stopwords_path = os.path.join(utils.get_root_path(), 'metadata_extractor/stopwords.txt')

    def extract(self, text, top_k=5, extract_mode='text_rank'):
        jieba.analyse.set_stop_words(self.stopwords_path)
        if extract_mode == 'tfidf':
            return jieba.analyse.extract_tags(text, topK=top_k, allowPOS=POS)
        elif extract_mode == 'text_rank':
            # text rank
            return jieba.analyse.textrank(text, topK=top_k, withWeight=False, allowPOS=POS)
        else:
            raise Exception('error extract_mode param provided, should be tfidf or text_rank')


if __name__ == '__main__':
    tag_extractor = TagExtractor()

    text = "美元指数回落至104下方，非美货币涨跌互现，人民币小幅贬值：人民币即期汇率收于7.1984（+57pips），日元-0.22%、韩元+0.33%、欧元+0.42%、加元+0.06%、澳元+0.83%、英榜+0.43%。"
    tags_tfidf = tag_extractor.extract(text, extract_mode='tfidf')
    print(tags_tfidf)
    tags_textrank = tag_extractor.extract(text, extract_mode='text_rank')
    print(tags_textrank)
