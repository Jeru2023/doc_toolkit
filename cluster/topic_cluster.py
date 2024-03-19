from sklearn.feature_extraction.text import CountVectorizer
import jieba
import re
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer

embedding_model = 'BAAI/bge-large-zh-v1.5'


class TopicCluster:

    @staticmethod
    def tokenize_zh(text):
        text = re.sub('\W*', '', text)
        words = jieba.lcut(text)
        # return ' '.join(words)
        return words

    def cluster(self, docs):
        content = '\n'.join(docs).strip()
        vectorizer = CountVectorizer(tokenizer=lambda x: self.tokenize_zh(x))
        topic_model = BERTopic(language="multilingual", embedding_model=embedding_model, verbose=True, vectorizer_model=vectorizer)

        sentence_model = SentenceTransformer(embedding_model)
        embeddings = sentence_model.encode(docs, show_progress_bar=False)
        topics, _ = topic_model.fit_transform(docs, embeddings=embeddings)
        return topics


if __name__ == '__main__':
    docs = [
        "12月12日，阳光电源公告，公司控股股东、实际控制人曹仁贤将其持有本公司的380万股股份办理了质押业务，目前合计质押公司股份3277万股，占其所持股比7.22%。",
        "这只是一个案例而已。实际上，曹仁贤近年来依托公司主业，围绕光伏与储能、半导体等产业链，全面展开个人投资业务，完全媲美顶级投资机构，堪称一代大师。",
        "今年的胡润百富榜上，阳光电源董事长曹仁贤及夫人苏蕾，以480亿位列第86位，蝉联安徽省首富。胡润百富统计曹老师的财富，只采集了其持有的阳光电源股权的信息，这其实并不全面。",
        "公司主要为银行、航空、保险、快消等行业的企业客户实施忠诚度计划提供服务。报告期内，公司对前五大客户（同一控制合并口径下）的销售金额占比分别为61.30%、66.91%及64.98%。",
        "永辉超市（601933）：拟向大连御锦贸易有限公司出售公司持有的万达商管1.43%股份。永辉超市公告，拟向大连御锦贸易有限公司出售公司持有的万达商管1.43%股份，转让价格为45.3亿元；截止至本公告日，该股权投资账面价值为39.18亿元。",
        "Nox聚星基于自身6300w+网红数据库，对东南亚、中东、北美、日韩、拉美五地区网红营销概况等相关数据进行分析，帮助中国出海品牌洞察行业营销趋势，助力品牌获得更好的营销效果。",
        "印尼作为东南亚最大经济体，具有较高的人口红利优势，集中了全东南亚超半数的网红；东南亚地区网红主要分布在印尼、泰国、越南三个国家；YouTube网红区域分布Instagram网红区域分布TikTok网红区域分布。",
        "从平均互动率、平均观看量、粉丝粘性三个数据维度上来看，YouTube综合表现明显优于TikTok、Instagram；虽然TikTok综合表现相较YouTube略微逊色，但随着TikTok在东南亚布局逐渐完善，相信其还存在着极大的增长潜力",
        "这家公司的困境说明了新冠病毒危机是如何撼动了亚洲电子供应链（亚洲电子供应链已经在过去的国际贸易新变数中受到了影响），以及中国工厂生态系统所扮演的不可或缺的角色。",
        "首先，最初的疫情爆发迫使其位于中国的工厂关闭了近三周，并导致中国工厂对本公司越南工厂的供应开始枯竭。然后，当病毒传播到韩国时，旅行限制阻止了其工人在位于港口城市海防的工厂继续提升产能。",
        "这就是三星的担忧所在，它建议员工不要在周末与家人和朋友外出，要求他们戴上口罩，相互交谈时保持2米以上的距离。",
        "根据极光iapp数据显示，从生鲜电商app渗透率来看，排名前五的主要是以线下社区型为主，包括生鲜O2O型、社区便利店和新零售，当然也包括部分仅有线上运营的前置仓模式的叮咚买菜和朴朴。",
        "可以预见的是，社区生鲜电商行业将是一场持久战，究其原因在于中国地域广阔，生鲜线下实体店/市场作为国民基础设施区域布局完善程度不同，各线城市对于生鲜需求倾向性有较大的区别。"
    ]

    topic_cluster = TopicCluster()
    topics = topic_cluster.cluster(docs)
    print(topics)
