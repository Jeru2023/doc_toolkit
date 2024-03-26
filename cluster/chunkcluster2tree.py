import numpy as np
from sentence_splitter.sentence_cutter import SentenceCutter
from topic_cluster import TopicCluster


class Cluster2Node(SentenceCutter):
    """
    定义节点类
    """

    def __init__(self, index, left=None, right=None, zh_min_len=30, **kwargs):
        self.index: int = index  # 节点索引
        self.left = left  # 左子节点
        self.right = right  # 右子节点
        # 节点基本信息
        self.word_cnt: int = 0  # 此节点下所有叶子节点的段落长度和
        self.leafs = []  # 存储节点下包含的所有叶子链接
        # # 叶节点特有信息
        # # 存储叶节点信息，比如{'index':xxx, 'text':'xxx', 'entities':[], 'core_entity':'xxx'}
        # self.leaf_index = kwargs.get('index', None)
        # self.leaf_text = kwargs.get('text', '')
        # self.leaf_entities = kwargs.get('entities', [])
        # self.leaf_core_entity = kwargs.get('core_entity', '')  # branch_core_entity不冲突

        # # 非叶节点特有信息
        # # {'top_5_entities':[], 'core_entity':'xxx', 'tags':[]}
        # self.branch_top_5_entities = kwargs.get('top_5_entities', [])
        # self.branch_core_entity = kwargs.get('core_entity', '')  # leaf_core_entity不冲突
        # self.branch_tags = kwargs.get('tags', [])

        self.zh_min_len = zh_min_len

    def __repr__(self):
        return f"Node(index={self.index}, word_cnt={self.word_cnt})"

    # def pp_para(self, para_text):
    #     """
    #     对para进行切分
    #     'sentence':{'subject':'xxx', entities:[], 'text':'xxx'}
    #     """
    #     return [
    #         {
    #             'subject': '',
    #             'entities': [],
    #             'text': sent
    #         } for sent in self.cut(para_text, zh_min_len=self.zh_min_len)
    #     ]

    # def pp_branch(self):
    #     """
    #     {'chunk':{'top_5_entities':[], 'core_entity':'xxx', 'tags':[],
    #         'paragraphs':[
    #                 {'index':xxx, 'text':'xxx', 'entities':[], 'core_entity':'xxx'}
    #             ,...]
    #     }
    #     """
    #     return {
    #         'chunk': {
    #             'core_entity': self.branch_core_entity,
    #             'top_5_entities': self.branch_top_5_entities,
    #             'tags': self.branch_tags,
    #             'paragraphs': [{
    #                 'index': paragraph.leaf_index,
    #                 'core_entity': paragraph.leaf_core_entity,
    #                 'entities': paragraph.leaf_entities,
    #                 'text': paragraph.leaf_text,
    #                 #'sentence': self.pp_para(paragraph.leaf_text)
    #             } for paragraph in self.leafs
    #             ]
    #         }
    #     }


class Cluster2Tree:
    """
    二分链表树
    """

    def __init__(self):
        # self.paragraphs = paragraphs
        # self.zh_min_len = zh_min_len
        self.topic_cluster = TopicCluster()
        # self.linkage_matrix = self.topic_cluster.cluster(self.paragraphs)
        # self.root = self.build_cluster_tree(self.linkage_matrix, self.paragraphs)

    @staticmethod
    def paragraphs2docs(paragraphs):
        """将paragraphs转换为docs格式，用于聚类入参"""
        # paragraphs.sort(key=lambda x: x['index'])
        docs = [''.join([sentence['text'] for sentence in paragraph['sentences']]) for paragraph in paragraphs]
        return docs

    def build_cluster_tree(self, paragraphs, chunk_size=2000) -> Cluster2Node:
        """
        构建链表: a -> b, c
        [[ 0,  1,  0.2,  2,]
         [ 2,  3,  0.5,  2,]
         [ 4,  5,  0.8,  4,]]
        """
        paragraphs.sort(key=lambda x: x['index'])
        docs = self.paragraphs2docs(paragraphs)
        linkage_matrix = self.topic_cluster.cluster(docs)
        node_a_index = node_cnt = len(linkage_matrix) + 1  # 初始化非叶节点索引
        nodes_dict = {}  # 临时存储节点列表，到root节点时，只有一个元素

        for row in linkage_matrix:
            # 分支节点
            if (node_b := int(row[0])) < node_cnt:  # 叶子节点
                left_node = Cluster2Node(node_b)
                left_node.word_cnt = len(docs[node_b])
                left_node.leafs = [node_b]
            else:
                left_node = nodes_dict[node_b]
                nodes_dict.pop(node_b)
            if (node_c := int(row[1])) < node_cnt:  # 叶子节点
                right_node = Cluster2Node(node_c)
                right_node.word_cnt = len(docs[node_c])
                right_node.leafs = [node_c]
            else:
                right_node = nodes_dict[node_c]
                nodes_dict.pop(node_c)

            # 创建父节点
            node_a = Cluster2Node(
                node_a_index,
                left=left_node,
                right=right_node,
            )
            node_a.word_cnt = left_node.word_cnt + right_node.word_cnt
            node_a.leafs = left_node.leafs + right_node.leafs
            node_a.leafs.sort(key=lambda x: x.index)

            node_a_index += 1  # 下一个父节点index+1
            nodes_dict.update({node_a.index: node_a})

        # 聚类树root生成
        root = nodes_dict.popitem()[1]

        return self.cut(root, chunk_size=chunk_size)

    def cut(self, root, chunk_size=2000) -> list[Cluster2Node]:
        """
        从任一节点递归遍历，做2000字内切分
        """
        if root.word_cnt <= chunk_size or len(root.leafs) == 1:
            return [root]
        return self.cut(root.left) + self.cut(root.right)

    # def __repr__(self):
    #     return f"Node(index={self.root.index}, word_cnt={self.root.word_cnt})"


if __name__ == '__main__':

    paragraphs = [
        {'index': 0, 'sentences': [{'text': '我爱北京天安门。'}, {'text': '天安门上太阳升。'}, {'text': '天安门上太阳升。'}, {'text': '天安门上太阳升。'},]},
        {'index': 1, 'sentences': [{'text': '我爱北京天安门2。'}, {'text': '天安门上太阳升2。'}, {'text': '天安门上太阳升2。'}, {'text': '天安门上太阳升2。'},]}
    ]

    # 构建链表
    ct = Cluster2Tree()
    # 打印根节点信息
    print(ct.build_cluster_tree(paragraphs, chunk_size=10))

    # # 按2000字切分链表
    # # [print(node.leafs) for node in ct.cut_tree(limit_cut=2000)]
    # [print(node.pp_branch()) for node in ct.cut_tree(chunk_size=2000)]
