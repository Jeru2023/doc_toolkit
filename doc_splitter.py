from paragraph_splitter.paragraph_cutter import ParagraphCutter
from sentence_splitter.sentence_cutter import SentenceCutter
from metadata_extractor.tag_extractor import TagExtractor
from metadata_extractor.entity_extractor import EntityExtractor
from cluster.topic_cluster import TopicCluster
from cluster.chunk_cluster_tree import Cluster2Tree
from grammar.analyzer import GrammarAnalyzer
from collections import defaultdict
from tools.utils import timer
import warnings

warnings.filterwarnings("ignore")  # Suppress all warnings
ENTITY_TYPES = ['技术名', '公司名', '产品名', '行业名']


class DocSplitter:
    def __init__(self):
        self.paragraph_cutter = ParagraphCutter()
        self.sentence_cutter = SentenceCutter()
        self.topic_cluster = TopicCluster()
        self.tag_extractor = TagExtractor()
        self.entity_extractor = EntityExtractor()
        self.grammar_analyzer = GrammarAnalyzer()
        self.chunk_cluster_tree = Cluster2Tree()

    @timer
    def append_metadata_to_sentence(self, paragraphs):
        for paragraph in paragraphs:
            for sentence in paragraph['sentences']:
                entities = self.entity_extractor.extract(sentence['text'])
                sentence['entities'] = entities

                entity_subject, coref_subject = self.grammar_analyzer.find_subject(sentence['text'], entities)
                sentence['entity_subject'] = entity_subject
                sentence['coref_subject'] = coref_subject

    def append_tags_to_chunk(self, doc, chunks):
        paragraphs = [chunk["paragraphs"] for chunk in chunks]
        flattened_list = [item for sublist in paragraphs for item in sublist]
        docs = self.merge_paragraph_text(flattened_list)

        # docs = self.chunk_cluster_tree.paragraphs2docs(flattened_list)
        tfidf_matrix = self.topic_cluster.get_tfidf_matrix(docs)

        vocab = self.topic_cluster.tokenizer(docs)

        i = 0
        for chunk in chunks:
            # 提取当前 chunk 的 TF-IDF 向量
            chunk_tfidf = tfidf_matrix[:, chunk.start:chunk.end]

            # 计算每个词在当前 chunk 中的 TF-IDF 权重之和
            chunk_weights = chunk_tfidf.sum(axis=0).A1

            # 获取前 10 个关键词的索引
            top_keywords_indices = chunk_weights.argsort()[-10:][::-1]

            # 根据索引获取对应的关键词
            top_keywords = [vocab[idx] for idx in top_keywords_indices]

            # chunk_text = self.merge_paragraph_text(chunk['paragraphs'])
            # tags = self.tag_extractor.extract(''.join(chunk_text), extract_mode='tfidf', top_k=10)
            chunk['tags'] = top_keywords
            i += 1

    @staticmethod
    @timer
    def merge_paragraph_text(paragraph_list):
        """合并每个段落的句子文本。

        Args:
          paragraph_list: 一个字典列表，其中每个字典代表一段，包含 `sentences` 键，
            其值为一个句子列表。

        Returns:
          一个包含合并后段落文本的列表。
        """
        merged_texts = []
        for paragraph in paragraph_list:
            sentences = paragraph['sentences']
            merged_text = ' '.join([sentence['text'] for sentence in sentences])
            merged_texts.append(merged_text)

        return merged_texts

        # 合并字典
    @staticmethod
    def merge_dicts(dicts):
        merged = defaultdict(dict)
        for d in dicts:
            for key, value in d.items():
                if isinstance(value, dict):
                    for inner_key, inner_value in value.items():
                        merged[key][inner_key] = merged[key].get(inner_key, 0) + inner_value
                else:
                    merged[key] = value
        return merged

    def merge_sentence_entity_to_paragraph(self, paragraphs):
        for paragraph in paragraphs:
            paragraph_entities = []
            for sentence in paragraph['sentences']:
                # exclude time and location entities
                sentence_entities = [e for e in sentence['entities'] if '时间' not in e and '地点' not in e]
                paragraph_entities.extend(sentence_entities)

            entities = self.merge_dicts(paragraph_entities)
            paragraph['entities'] = [dict(entities)]

    def merge_paragraph_entity_to_chunk(self, chunks):
        for chunk in chunks:
            chunk_entities = []
            for paragraph in chunk['paragraphs']:
                entity_list = paragraph['entities']
                chunk_entities.extend(entity_list)

            entities = self.merge_dicts(chunk_entities)

            chunk['entities'] = [dict(entities)]

    def split(self, doc, chunk_size=1000, with_entities=True, with_tags=True):
        # paragraph_texts as a list of text
        paragraph_texts = self.paragraph_cutter.cut(doc.replace('\n', ''))
        # paragraphs as a list of dict
        paragraphs = self.paragraph_cutter.get_paragraphs_node(paragraph_texts)

        if with_entities:
            self.append_metadata_to_sentence(paragraphs)
            self.merge_sentence_entity_to_paragraph(paragraphs)

        # 构建链表
        chunks = self.chunk_cluster_tree.build_cluster_tree(paragraphs, chunk_size)

        if with_entities:
            self.merge_paragraph_entity_to_chunk(chunks)

        if with_tags:
            self.append_tags_to_chunk(doc, chunks)

        return chunks

    # 获取前 n 个高频词及其频次
    @staticmethod
    def get_top_n_entities(merged_dict, n):
        word_freq = defaultdict(int)
        for key, value in merged_dict.items():
            if key in ENTITY_TYPES:
                if isinstance(value, dict):
                    for word, freq in value.items():
                        word_freq[word] += freq
                else:
                    word_freq[key] += value

        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        top_n_words = dict(sorted_words[:n])
        return top_n_words

    @staticmethod
    # 获取频次最高的公司名
    def get_top_company(merged_dict):
        company_freq = defaultdict(int)
        if '公司名' in merged_dict:
            for company, freq in merged_dict['公司名'].items():
                company_freq[company] += freq
        sorted_companies = sorted(company_freq.items(), key=lambda x: x[1], reverse=True)
        if sorted_companies:
            top_company = sorted_companies[0][0]
            return top_company
        else:
            return None

    def append_entities_to_paragraph(self, nodes):
        for node in nodes:
            chunk = node['chunk']
            paragraphs = chunk['paragraphs']

            chunk_entities = []
            for paragraph in paragraphs:
                entities = self.entity_extractor.extract(paragraph['text'])
                paragraph['entities'] = entities

                for entity in entities:
                    if '公司名' in entity:
                        paragraph['core_entity'] = entity['公司名']

                # aggregate entities from paragraphs for each chunk
                chunk_entities.extend(paragraph['entities'])

            # merge entities from paragraphs for each chunk
            merge_dicts = self.merge_dicts(chunk_entities)

            chunk['top_5_entities'] = self.get_top_n_entities(merge_dicts, 5)
            chunk['core_entity'] = self.get_top_company(merge_dicts)

        return nodes
