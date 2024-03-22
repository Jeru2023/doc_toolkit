from paragraph_splitter.paragraph_cutter import ParagraphCutter
from metadata_extractor.tag_extractor import TagExtractor
from cluster.topic_cluster import TopicCluster
from cluster.cluster2tree import Cluster2Tree
import warnings

warnings.filterwarnings("ignore")  # Suppress all warnings


class DocSplitter:
    def __init__(self):
        self.paragraph_cutter = ParagraphCutter()
        self.topic_cluster = TopicCluster()
        self.tag_extractor = TagExtractor()

    def split(self, doc, chunk_size=2000):
        paragraphs = self.paragraph_cutter.cut(doc)
        docs = [paragraph['text'] for paragraph in paragraphs]

        linkage_matrix = self.topic_cluster.cluster(docs)

        # 构建链表
        cluster_tree = Cluster2Tree(linkage_matrix, docs)

        # 按 chunk_size 长度切分链表
        nodes = [(node.pp_branch()) for node in cluster_tree.cut_tree(chunk_size=chunk_size)]
        return nodes

    def append_tags_to_cluster(self, nodes, extract_mode='tfidf', top_k=10):
        for node in nodes:
            chunk = node['chunk']
            paragraphs = chunk['paragraphs']

            node_text = ''.join([paragraph['text'] for paragraph in paragraphs])
            chunk['tags'] = self.tag_extractor.extract(node_text, extract_mode=extract_mode, top_k=top_k)

        return nodes
