import jieba.analyse

#POS = ('n', 'nz', 'v', 'vd', 'vn', 'l', 'a', 'd')
POS = ('n', 'nz', 'ns', 'nt', 'nr', 'l')


class TagExtractor:

    @staticmethod
    def extract(text, top_k=5):
        tags = jieba.analyse.extract_tags(text, topK=top_k, allowPOS=POS)
        return tags
