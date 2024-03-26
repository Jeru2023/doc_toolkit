import doc_splitter
from tools import utils
from metadata_extractor.tag_extractor import TagExtractor
from keybert import KeyBERT
import spacy
from cluster.topic_cluster import TopicCluster

kw_model = KeyBERT(model='BAAI/bge-large-zh-v1.5')

doc_name = '西典新能招股书.txt'
#doc_name = '中创股份研报.txt'
doc = utils.load_text(doc_name)

doc_splitter = doc_splitter.DocSplitter()
chunks = doc_splitter.split(doc, 2000, with_entities=False)
tag_extractor = TagExtractor()

topic_cluster = TopicCluster()

nlp = spacy.load("zh_core_web_sm")
kw_model_word = KeyBERT(model=nlp)


i = 0
for chunk in chunks:
    print('*** chunk {i} ***'.format(i=i))
    print('================================\n')
    # join text in paragraphs
    para_texts = doc_splitter.merge_paragraph_text(chunk['paragraphs'])
    chunk_text = ''.join(para_texts)
    print(chunk_text)
    print(f'text rank tags: {tag_extractor.extract(chunk_text, extract_mode="text_rank", top_k=10)}')
    print(f'tfidf tags: {tag_extractor.extract(chunk_text, extract_mode="tfidf", top_k=10)}')

    word_list = topic_cluster.tokenizer(chunk_text)
    words = kw_model_word.extract_keywords(' '.join(word_list), keyphrase_ngram_range=(1, 2), top_n=10)
    print(f'keybert words tags with BGE: {words}')
    phrases = kw_model.extract_keywords(' '.join(word_list), keyphrase_ngram_range=(1, 2), top_n=10)
    print(f'keybert words tags with spacy: {phrases}')

    i += 1
