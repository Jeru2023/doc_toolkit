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
        'sentences':{'subject':'xxx', entities:[], 'text':'xxx'}
        """
        return [
            {
                'subject': '',
                'entities': [],
                'text': sentence
            } for sentence in self.sentence_cutter.cut(text, zh_min_len=10)
        ]

    @staticmethod
    def fill_paragraph(index):
        return {
            'index': index,
        }

    @timer
    def cut(self, text, split_mode='bert', chunk_size=800):
        """
        :param text: text to be cut
        :param split_mode: 'bert', 'natural' or 'brutal'
        :param chunk_size: applicable only for 'brutal'
        :return: a list of dictionaries, each dictionary represents a paragraph
        """

        if split_mode == 'bert':
            bert_cutter = BertCutter()
            paragraphs = bert_cutter.cut(text)
        elif split_mode == 'natural':
            natural_cutter = NaturalCutter()
            paragraphs = natural_cutter.cut(text)
        elif split_mode == 'brutal':
            brutal_cutter = BrutalCutter()
            paragraphs = brutal_cutter.cut(text, chunk_size)
        else:
            # raise exception of error mode param
            raise Exception('error split_mode param provided, should be bert, natural or brutal')

        chunks = []
        for index, paragraph in enumerate(paragraphs):
            chunk = self.fill_paragraph(index)
            chunk.update({"sentences": self.fill_sentences(paragraph)})

            chunks.append(chunk)

        return chunks
