from paragraph_splitter.paragraph_cutter import ParagraphCutter
from metadata_extractor.tag_extractor import TagExtractor
from metadata_extractor.entity_extractor import EntityExtractor
from cluster.topic_cluster import TopicCluster
from cluster.cluster2tree import Cluster2Tree
from collections import defaultdict
import json
import warnings

warnings.filterwarnings("ignore")  # Suppress all warnings
ENTITY_TYPES = ['技术名', '公司名', '产品名', '行业名']


class DocSplitter:
    def __init__(self):
        self.paragraph_cutter = ParagraphCutter()
        self.topic_cluster = TopicCluster()
        self.tag_extractor = TagExtractor()
        self.entity_extractor = EntityExtractor()

    def split(self, doc, chunk_size=2000):
        paragraphs = self.paragraph_cutter.cut(doc)
        docs = [paragraph['text'] for paragraph in paragraphs]

        linkage_matrix = self.topic_cluster.cluster(docs)

        # 构建链表
        cluster_tree = Cluster2Tree(linkage_matrix, docs)

        # 按 chunk_size 长度切分链表
        nodes = [(node.pp_branch()) for node in cluster_tree.cut_tree(chunk_size=chunk_size)]
        return nodes

    @staticmethod
    def merge_dict(dict1, dict2):
        merged_dict = {}
        for key, value in dict1.items():
            if key in dict2:
                merged_dict[key] = value + dict2[key]
            else:
                merged_dict[key] = value
        for key, value in dict2.items():
            if key not in merged_dict:
                merged_dict[key] = value
        return merged_dict

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

    def append_tags_to_cluster(self, nodes, extract_mode='tfidf', top_k=10):
        for node in nodes:
            chunk = node['chunk']
            paragraphs = chunk['paragraphs']

            node_text = ''.join([paragraph['text'] for paragraph in paragraphs])
            chunk['tags'] = self.tag_extractor.extract(node_text, extract_mode=extract_mode, top_k=top_k)

        return nodes


