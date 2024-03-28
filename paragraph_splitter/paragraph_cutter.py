from paragraph_splitter.bert_cutter import BertCutter
from paragraph_splitter.brutal_cutter import BrutalCutter
from paragraph_splitter.natural_cutter import NaturalCutter
from sentence_splitter.sentence_cutter import SentenceCutter
from tools.utils import timer


class ParagraphCutter:
    def __init__(self):
        self.sentence_cutter = SentenceCutter()

    def fill_sentences(self, text):
        """
        对paragraph进行切分
        'sentences':{'subject_entity':'xxx', entities:[], 'text':'xxx'}
        """
        return [
            {
                'entity_subject': '',
                'coref_subject': '',
                'entities': [],
                'text': sentence
            } for sentence in self.sentence_cutter.cut(text, mode='fine')
        ]

    @staticmethod
    def fill_paragraph(index):
        return {
            'index': index,
        }

    @timer
    def cut(self, text, split_mode='bert', para_size=800):
        """
        :param text: text to be cut
        :param split_mode: 'bert', 'natural' or 'brutal'
        :param para_size: applicable only for 'brutal'
        :return: a list of paragraph text
        """

        if split_mode == 'bert':
            bert_cutter = BertCutter()
            paragraphs = bert_cutter.cut(text)
        elif split_mode == 'natural':
            natural_cutter = NaturalCutter()
            paragraphs = natural_cutter.cut(text)
        elif split_mode == 'brutal':
            brutal_cutter = BrutalCutter()
            paragraphs = brutal_cutter.cut(text, para_size)
        else:
            # raise exception of error mode param
            raise Exception('error split_mode param provided, should be bert, natural or brutal')

        return paragraphs

    @timer
    def get_paragraphs_node(self, paragraphs):
        """
        :param paragraphs: a list of paragraph text
        :return: a list of dictionaries, each dictionary represents a paragraph
        """
        nodes = []
        for index, paragraph in enumerate(paragraphs):
            node = self.fill_paragraph(index)
            node.update({"sentences": self.fill_sentences(paragraph)})

            nodes.append(node)

        return nodes
