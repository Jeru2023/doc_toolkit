# -*- encoding: utf-8 -*-
from ltp import LTP


class GrammarAnalyzer:
    def __init__(self):
        self.ltp = LTP()

    @staticmethod
    def get_company_names(entities):
        company_names = []

        for entity in entities:
            for key, value in entity.items():
                if key == '公司名':
                    for company_name in value.keys():
                        company_names.append(company_name)
        return company_names

    def parse_query(self, query, company_names):
        self.ltp.add_words(company_names, freq=2)
        output = self.ltp.pipeline([query], tasks=["cws", "dep"])
        cws = output.cws[0]
        dep = output.dep[0]['label']
        return cws, dep

    def find_subject_entity(self, text, entities):
        company_names = self.get_company_names(entities)
        cws, dep = self.parse_query(text, company_names)

        sbv_word = None
        for i, dep_tag in enumerate(dep):
            if (dep_tag == 'SBV') and (cws[i] in company_names):
                sbv_word = cws[i]
                break
        return sbv_word


if __name__ == '__main__':
    texts = [
        """同行业上市公司对比：公司主要从事中间件软件的研发、销售，并提供相关技术服务，因此选取同样从事中间件软件研销的东方通、宝兰德作为中创股份的可比公司，但考虑到上述公司的业务结构与公司存在差异，我们倾向于认为上述公司的可比性或相对有限。""",
        "专业中间件行业呈现较好的竞争格局，主流厂商包括东方通、中创、宝兰德、普元、金蝶等已树立起一定的竞争壁垒",
        #"""公司曾多次牵头承担“核高基”科技重大专项、且曾负责工信部项目D，所形成的产品通过信创工程已率先在党政、军工等领域实现国产中间件替换，
        #产品服务于中共中央办公厅、国家发改委、水利部、银保监会等重点单位及中国银行、潍柴动力、南方电网等重点行业龙头客户，在党政、军工领域具备较强的竞争优势。"""
    ]

    grammar_analyzer = GrammarAnalyzer()

    _entities = [{'公司名': {'东方通': 1, '宝兰德': 1}}]

    for _text in texts:
        _subject_entity = grammar_analyzer.find_subject_entity(_text, _entities)
        print('Subject is: ', _subject_entity)


