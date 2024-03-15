from sentence_splitter.sentence_cutter import SentenceCutter
from metadata_extractor.tag_extractor import TagExtractor


class ParagraphCutter:
    def __init__(self):
        self.sentence_cutter = SentenceCutter()
        self.tag_extractor = TagExtractor()

    def cut(self, text, max_length=300):
        sentences = self.sentence_cutter.cut(text)

        paragraphs = []
        for sentence in sentences:
            if not paragraphs:
                paragraphs.append(sentence)
            else:
                if len(paragraphs[-1]) + len(sentence) < max_length:
                    paragraphs[-1] += sentence
                else:
                    paragraphs.append(sentence)

        return paragraphs


if __name__ == '__main__':
    pc = ParagraphCutter()

    text = """
    3月11日，美指上周正如预期向下运行，最低102.30附近，周图收阴柱。从图形来看，后市重点关注下方101.70强支撑区域，若能成功跌破，美指将深跌至98.30和97.30附近的概率将加大好多；反则关注向上反弹行情。本周主要为震荡格局行情，在上方103.60以下还是偏空头，看是反弹后继续跌，还是反弹变反转站稳103.60上方，向上测试105.80附近。实战操作上，建议反弹修整后，在103.20-103.40区域做空，止损104.10，目标看向102.80和102.40，再看向102.20和101.70附近。控制仓量，严格止损。

欧元上周正如预期向上运行，目标位1.0950也已到达，周图收阳柱。从图形来看，欧元下个波段上方关注1.1030和1.1050附近，这个区域若能成功站稳上方，欧元向上方1.1490区域逼近的概率将加大好多，反则承压向下回落测试1.0620区域。本周初先关注高位修整震荡行情，再关注下一步走势，短期看，本周在1.0880以上还是偏多头，操作建议：1.0880-1.0910区域做多，止损1.0820，目标看向1.0990，再看向1.1030和1.1050区域。控制仓量，严格止损。

黄金上周正如预期向上运行，最高2195附近，比预测的2110还高了80美金，黄金这波涨幅超预期。从目前图形来看，2184也到位了，近期是不建议再做多了，长线最远我只能看到2250附近，预期节奏两波震荡拉涨行情上来的，第一波先到2110附近，第二波才能拉到2250附近。但实际走势直线拉涨波幅太大，所以这波2184就差不多了，以上就是逼空行情，随时有可能向下回落，这是我分析出来的结果，至于对不对不确定，要等市场给答案。后市近期以修整行情为主，高位震荡或震荡下行修整，都是正常的，建议保守者选择观望不操作，等行情明朗了再继续。

白银正如预期向上运行，最高24.60附近，周图收阳柱。从图形来看，白银后市23，50以上继续看涨，目标25和25.50附近。实战操作可等待24.60-23.50震荡修整完结后再进场，若不向下回调，不建议高位追多，风险较大。本周只有框架思路，没有具体操作建议。
    """
    results = pc.cut(text)
    print(results)
