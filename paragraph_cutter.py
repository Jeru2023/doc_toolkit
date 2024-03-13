class ParagraphCutter:

    @staticmethod
    def cut(text):
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        return paragraphs


if __name__ == '__main__':
    pc = ParagraphCutter()

    text = """
    万壑树参天，千山响杜鹃。山中一夜雨，树杪百重泉。
    汉女输橦布，巴人讼芋田。文翁翻教授，不敢倚先贤。
    """

    results = pc.cut(text)
    print(results)
