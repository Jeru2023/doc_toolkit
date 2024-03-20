class NaturalCutter:

    @staticmethod
    def cut(text):
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        return paragraphs


if __name__ == '__main__':
    nc = NaturalCutter()

    text = """
    万壑树参天，千山响杜鹃。山中一夜雨，树杪百重泉。
    汉女输橦布，巴人讼芋田。文翁翻教授，不敢倚先贤。
    """

    results = nc.cut(text)
    print(results)
