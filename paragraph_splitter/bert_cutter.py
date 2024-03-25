# -*- encoding: utf-8 -*-
from modelscope.utils.import_utils import LazyImportModule
LazyImportModule.AST_INDEX['index'][('PIPELINES', 'document-segmentation', 'document-segmentation')] = {
    'module': 'local_modelscope.pipelines.nlp.document_segmentation_pipeline'}
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
from tools.utils import timer


class BertCutter:

    @staticmethod
    @timer
    def cut(text):
        p = pipeline(
            task=Tasks.document_segmentation,
            # task=Tasks.document_segmentation,
            model='damo/nlp_bert_document-segmentation_chinese-base')

        text = text.replace('\n', '')
        output = p(documents=text)['text']
        paragraphs = [p.strip() for p in output.split('\n\t') if p.strip()]

        return paragraphs


if __name__ == '__main__':
    bc = BertCutter()

    from tools import utils

    doc_name = '../examples/中创股份研报.txt'
    doc = utils.load_text(doc_name)

    results = bc.cut(doc)
    print(results)
