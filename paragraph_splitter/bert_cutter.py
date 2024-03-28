# -*- encoding: utf-8 -*-
from modelscope.utils.import_utils import LazyImportModule
LazyImportModule.AST_INDEX['index'][('PIPELINES', 'document-segmentation', 'document-segmentation')] = {
    'module': 'local_modelscope.pipelines.nlp.document_segmentation_pipeline'}
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
from tools.utils import timer


class BertCutter:

    def __init__(self):
        self.p = pipeline(
            task=Tasks.document_segmentation,
            model='damo/nlp_bert_document-segmentation_chinese-base')

    @timer
    def cut(self, text):

        text = text.replace('\n', '')
        output = self.p(documents=text)['text']
        paragraphs = [p.strip() for p in output.split('\n\t') if p.strip()]

        return paragraphs


if __name__ == '__main__':
    bc = BertCutter()

    from tools import utils

    doc_name = '../examples/新闻原始数据底层.txt'
    doc = utils.load_text(doc_name)

    results = bc.cut(doc)
    print(results)

    doc_name = '../examples/新闻原始数据底层.txt'
    doc = utils.load_text(doc_name)

    results = bc.cut(doc)
    print(results)

    doc_name = '../examples/新闻原始数据底层.txt'
    doc = utils.load_text(doc_name)

    results = bc.cut(doc)
    print(results)



