from paragraph_splitter.bert_cutter import BertCutter
from paragraph_splitter.brutal_cutter import BrutalCutter
from paragraph_splitter.natural_cutter import NaturalCutter
from metadata_extractor.tag_extractor import TagExtractor
from metadata_extractor.entity_extractor import EntityExtractor
from tools.utils import timer


class ParagraphCutter:
    @staticmethod
    @timer
    def cut(text, split_mode='bert', with_tags=False, with_entities=False, chunk_size=800,
            top_k=5, extract_mode='text_rank'):
        """
        :param text: text to be cut
        :param split_mode: 'bert', 'natural' or 'brutal'
        :param with_tags: if keyword tags required.
        :param with_entities: if entity extraction required
        :param chunk_size: applicable only for 'brutal'
        :param top_k: number of tags to extract
        :param extract_mode: 'text_rank' or 'tfidf'
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
        for paragraph in paragraphs:
            chunk = {"text": paragraph}
            if with_tags:
                tag_extractor = TagExtractor()
                tags = tag_extractor.extract(paragraph, extract_mode=extract_mode, top_k=top_k)
                chunk["tags"] = tags
            if with_entities:
                entity_extractor = EntityExtractor()
                entities = entity_extractor.extract(paragraph)
                chunk["entities"] = entities
            chunks.append(chunk)

        return chunks
