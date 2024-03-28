from word_splitter.word_cutter import WordCutter
from word_splitter.tfidf import TFIDF
from tools import utils
from paragraph_splitter.paragraph_cutter import ParagraphCutter
from doc_splitter import DocSplitter

paragraph_cutter = ParagraphCutter()
doc_splitter = DocSplitter()
tfidf = TFIDF()

doc_name = '花西子.txt'
doc = utils.load_text(doc_name)
paragraphs = paragraph_cutter.cut(doc.replace('\n', ''))
paragraphs_text_list = doc_splitter.merge_paragraph_text(paragraphs)

tfidf_matrix = tfidf.get_tfidf_matrix(paragraphs_text_list)

print(tfidf_matrix)
