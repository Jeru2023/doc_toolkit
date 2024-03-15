import json
from metadata_extractor.tag_extractor import TagExtractor

class ParagraphCutter:
    def __init__(self):
        self.tag_extractor = TagExtractor()

    def cut(self, text, with_tags=False):
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]

        chunks = []
        for paragraph in paragraphs:
            chunk = {"paragraph": paragraph}

            if with_tags:
                tags = self.tag_extractor.extract(paragraph)
                chunk["tags"] = tags

            chunks.append(chunk)

        return chunks


if __name__ == '__main__':
    pc = ParagraphCutter()

    text = """
    万壑树参天，千山响杜鹃。山中一夜雨，树杪百重泉。
    汉女输橦布，巴人讼芋田。文翁翻教授，不敢倚先贤。
    """

    results = pc.cut(text, with_tags=True)
    for result in results:
        print(result["paragraph"])
        print(result["tags"])
        print('----------------')
