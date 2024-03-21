from paragraph_splitter.paragraph_cutter import ParagraphCutter
from cluster.topic_cluster import TopicCluster
from cluster.cluster2tree import Cluster2Tree


class DocSplitter:
    def __init__(self):
        self.paragraph_cutter = ParagraphCutter()
        self.topic_cluster = TopicCluster()

    def split(self, doc, chunk_size=2000):
        paragraphs = self.paragraph_cutter.cut(doc)
        docs = [paragraph['text'] for paragraph in paragraphs]

        linkage_matrix = self.topic_cluster.cluster(docs)

        # 构建链表
        cluster_tree = Cluster2Tree(linkage_matrix, docs)

        # 按 chunk_size 长度切分链表
        nodes = [(node.pp_branch()) for node in cluster_tree.cut_tree(chunk_size=chunk_size)]
        return nodes

