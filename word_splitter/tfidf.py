from word_splitter.word_cutter import WordCutter
from sklearn.feature_extraction.text import TfidfVectorizer


class TFIDF:
    def __init__(self):
        self.word_cutter = WordCutter()

    def get_tfidf_matrix(self, docs):
        #tokenizer = self.word_cutter.cut(doc)
        # chosen n-gram of three words. It will produce phrases containing upto three words
        vectorizer = TfidfVectorizer(stop_words='english', tokenizer=self.word_cutter.cut, ngram_range=(1, 3))

        # fit the vectorizer to documents
        tfidf_matrix = vectorizer.fit_transform(docs)

        return tfidf_matrix
