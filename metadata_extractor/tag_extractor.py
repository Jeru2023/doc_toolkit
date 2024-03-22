import jieba.analyse

# POS = ('n', 'nz', 'v', 'vd', 'vn', 'l', 'a', 'd')
POS = ('n', 'nz', 'ns', 'nt', 'nr', 'l')


class TagExtractor:

    @staticmethod
    def extract(text, top_k=5, extract_mode='text_rank'):
        if extract_mode == 'tfidf':
            return jieba.analyse.extract_tags(text, topK=top_k, allowPOS=POS)
        elif extract_mode == 'text_rank':
            # text rank
            return jieba.analyse.textrank(text, topK=top_k, withWeight=False, allowPOS=POS)
        else:
            raise Exception('error extract_mode param provided, should be tfidf or text_rank')


if __name__ == '__main__':
    tag_extractor = TagExtractor()

    text = """
    我在八零年代当后妈#我在八零年代当后妈全集[话题]# #小红书追剧人[话题]# #一起追剧[话题]#我在八零年代当后妈全集;小红书追剧人;一起追剧
    """
    tags_tfidf = tag_extractor.extract(text, extract_mode='tfidf', top_k=10)
    print(' '.join(tags_tfidf))
    tags_textrank = tag_extractor.extract(text, extract_mode='text_rank', top_k=10)
    print(' '.join(tags_textrank))