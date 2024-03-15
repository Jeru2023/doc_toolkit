# -*- encoding: utf-8 -*-
from langdetect import detect

from sentence_splitter.logic_graph_en import long_cuter_en
from sentence_splitter.automata.state_machine import StateMachine
from sentence_splitter.automata.sequence import EnSequence
from sentence_splitter.logic_graph import long_short_cuter
from sentence_splitter.automata.sequence import StrSequence
import spacy
from utils import timer


class SentenceCutter:
    def __init__(self):
        self.nlp_en = spacy.load("en_core_web_sm")

    @staticmethod
    def cut_english_sentences(text):
        # 令句子长度不能小于5个单词
        long_machine_en = StateMachine(long_cuter_en(min_len=5))
        m_input = EnSequence(text)
        long_machine_en.run(m_input)
        sentences = m_input.sentence_list()
        return sentences

    @staticmethod
    def cut_chinese_sentences(text, min_len):
        # -- 初始化 状态机器 -- #
        cuter = StateMachine(long_short_cuter(hard_max=500, max_len=500, min_len=min_len))
        sequence = cuter.run(StrSequence(text))
        sentences = sequence.sentence_list()
        return sentences

    @timer
    def cut(self, text, zh_min_len=30):
        lang = detect(text)

        if lang.startswith('zh'):
            # 中文切句调用 cut_to_sentences
            sentences = self.cut_chinese_sentences(text, zh_min_len)
        elif lang == 'en':
            # 英文切句调用 Spacy
            doc = self.nlp_en(text)
            sentences = [sent.text for sent in doc.sents]
        else:
            return []
        return [s.strip() for s in sentences]


if __name__ == '__main__':
    sc = SentenceCutter()
    paragraph = [
        # "在很久很久以前......。。... 有座山，山里有座庙啊!!!!!!!庙里竟然有个老和尚！？。。。。",
        # "A long time ago..... there is a mountain, and there is a temple in the mountain!!! And here is an old monk in the temple!?....",
        # "“我和你讨论的不是一个东西，死亡率与死亡比例是不同的”，“你知道么？CNN你们总是制造假新闻。。。”",
        # "张晓风笑着说道，“我们这些年可比过去强多了！“过去吃不起饭，穿不暖衣服。 现在呢？要啥有啥！",
        # "\"What would a stranger do here, Mrs. Price?\" he inquired angrily, remembering, with a pang, that certain new, unaccountable, engrossing emotions had quite banished Fiddy from his thoughts and notice, when he might have detected the signs of approaching illness, met them and vanquished them before their climax.",
        # "Notice that U.S.A. can also be written USA, but U.S. is better with the periods. Also, we can use U.S. as a modifier (the U.S. policy on immigration) but not as a noun (He left the U.S. U.S.A.).",
        # "万壑树参天，千山响杜鹃。山中一夜雨，树杪百重泉。汉女输橦布，巴人讼芋田。文翁翻教授，不敢倚先贤。",
        # "美元指数回落至104下方，非美货币涨跌互现，人民币小幅贬值：人民币即期汇率收于7.1984（+57pips），日元-0.22%、韩元+0.33%、欧元+0.42%、加元+0.06%、澳元+0.83%、英榜+0.43%。",
        """
山西煤炭主动控产，供给约束再趋紧煤炭开采。
山西煤炭主动控产，供给约束再趋紧。
本期内容提要：本周产地煤价涨跌互现。截至2月23日，陕西榆林动力块煤（Q6000）坑口价985.0元/吨，周环比持平；内蒙古东胜大块精煤车板价（Q5500）753.5元/吨，周环比下跌1.8元/吨；大同南郊粘煤坑口价（含税）（Q5500）765.0元/吨，周环比上涨17.0元/吨。
内陆电煤日耗环比增加。截至2月23日，本周秦皇岛港铁路到车3885车，周环比下降20.45%；秦皇岛港口吞吐35.3万吨，周环比下降2.75%。国内重要港口（秦皇岛、曹妃甸、国投京唐港）周内库存水平均值1071.56万吨，较上周的944.29万吨上涨127.3万吨，周环比增加13.48%。截至2月22日，内陆十七省煤炭库存7400.60万吨，较上周下降519.80万吨，周环比下降6.56%；日耗为404.20万吨，较上周上升21.00万吨/日，周环比增加5.48%；可用天数为18.3天，较上周下降2.40天。
国际动力煤价格环比上涨。港口动力煤：截至2月23日，秦皇岛港动力煤(Q5500)山西产市场价933.0元/吨，周上涨24.0元/吨。截至2月23日，纽卡斯尔NEWC5500大卡动力煤F0B现货价格97.5美元/吨，周环比上涨0.5美元/吨；ARA6000大卡动力煤现货价94.0美元/吨，周环比上涨2.0美元/吨；理查兹港动力煤F0B现货价82.8美元/吨，周环比上涨1.4美元/吨。。
焦炭方面：刚需恢复缓慢，焦炭依旧承压。产地指数：截至2024年2月23日，汾渭CCI吕梁准一级冶金焦报2010元/吨，周环比下降100元/吨。港口指数：CCI日照准一级冶金焦报2200元/吨，周环比上涨20元/吨。综合来看，焦炭市场偏弱运行，受三轮提降影响，焦企亏损加剧，多数企业维持前期限产幅度，少数企业有加大限产行为，且目前市场情绪悲观，价格仍有下调预期，供应端或将继续收紧；需求方面，下游成材库存堆积，库存压力较大，影响高炉复产放缓，焦炭日耗维持低位，原料采购相对谨慎；整体来看，焦炭市场供需结构宽松，后期需关注高炉复产节奏及钢焦企业成本变动。
焦煤方面：原料运输稍有好转，市场成交依旧冷清。截止2月23日，CCI山西低硫指数2430元/吨，日环比持平；CCI山西高硫指数2150元/吨，日环比持平；CCI灵石肥煤指数2150元/吨，日环比持平。本周复产煤矿陆续恢复出煤，产地供应稳步回升中，但整体产量仍然偏低，前期主产地普降大雪导致汽运基本停滞，部分地区经昨日天气转晴后，运输稍有好转。需求端，终端依旧亏损，焦价下行预期仍存，原料端持续观望，线上竞拍流拍率居高不下，其余成交也多以降价成交为主，煤矿坑口报价多数偏稳，部分高价资源有一定回调预期，焦煤市场整体偏弱运行。
策面共振，现阶段逢低配置煤炭板块正当时。供给方面，煤炭产地安全生产形势依旧严峻复杂，煤矿安全事故及死亡人数维持较高水平。需求方面，本周，受寒潮等因素影响，电煤日耗环比上升（截至2月22日，内陆十七省煤炭日耗为404.20万吨，较上周上升21.00万吨/日，周环比增加5.48%；沿海八省煤炭日耗为197.60万吨，较上周上升30.00万吨/日，周环比增加17.90%），仍处于历史较高水平；非电需求尤其是化工耗煤依旧旺盛（截至2月23日，化工周度耗煤为633.62万吨，较上周下降9.15万吨/日，周环比下降1.42百分点）。整体上，本周产地供应稳步回升（汾渭统计本周样本煤矿原煤产量周环比增加75.08万吨至736.84万吨，产能利用率周环比上升7.46%至73.18%），但仍未恢复至正常开工水平，预计元宵节后会集中复产。库存方面，受降雪影响，大部分煤矿汽运受限，煤矿库存增加；港口铁路发运量较节日期间有所好转，但仍然处于偏低水平，但港口近期封航频繁，节后北方港口库存快速累积。需求方面，元宵节后下游复工复产进程加快，需求仍有提升可能，短期价格仍易涨难跌。值得关注的是，近期，山西省发布《关于开展煤矿“三超"和隐蔽工作面专项整治的通知》，特别提到煤矿的超能力下达生产经营指标情况、煤矿超能力生产情况（全年原煤产量是否超过核定（设计）生产能力幅度的10%、月度原煤产量是否大于核定（设计）生产能力的10%）、采掘接续紧张情况、布置隐蔽工作面情况等。根据我们测算，2023年山西省煤炭产能约12.1亿吨，当年山西省生产煤炭13.6亿吨，超产1.5亿吨，超产比例12.4%，大于要求的10%，若按照《通知》要求，2024年至少有2.4%的产量压减空间，即山西省至少要减产3000-4000万吨，煤炭特别是炼焦煤供给面临较大收缩。整体上，我们认为煤炭供需两端供给最为关键，供给无弹性而需求有弹性，伴随需求的持续增长进而带来供给的压力和供需缺口的劣化，即本轮煤炭产能周期、供给约束带来的高景气周期仍在早中期。基于此，尽管过去三年煤炭板块已有一定涨幅，但尚未充分反映产能周期的底层逻辑以及资源实际价值，而本轮煤炭超额收益也不仅来自于“高股息”策略在熊市中的应用，其根本原因是产能周期下的供需错配带来的上涨，产业逻辑或仍将助推煤炭板块在熊市结束后有不错表现。总体上，能源大通胀背景下，我们认为未来3-5年煤炭供需偏紧的格局仍未改变，优质煤炭企业依然具有高壁垒、高现金、高分红、高股息的属性，叠加煤价筑底推动板块估值重塑，板块投资攻守兼备且具有高性价比，再度提示板块逢低配置。
风险因素：重点公司发生煤矿安全生产事故；下游用能用电部门继续较大规模限产：宏观经济大幅失速下滑。
我们认为，当前正处在煤炭经济新一轮周期上行的初期，基本面、政策面共振，现阶段逢低配置煤炭板块正当时供给方面，煤炭产地安全生产形势依旧严峻复杂，煤矿安全事故及死亡人数维持较高水平。需求方面，本周，受寒潮等因素影响，电煤日耗环比上升（截至2月22日，内陆十七省煤炭日耗为404.20万吨，较上周上升21.00万吨/日，周环比增加5.48%；沿海八省煤炭日耗为197.60万吨，较上周上升30.00万吨/日，周环比增加17.90%）仍处于历史较高水平；非电需求尤其是化工耗煤依旧旺盛（截至2月23日，化工周度耗煤为633.62万吨，较上周下降9.15万吨/日，周环比下降1.42百分点）。整体上，本周产地供应稳步回升（汾渭统计本周样本煤矿原煤产量周环比增加75.08万吨至736.84万吨，产能利用率周环比上升7.46%至73.18%），但仍未恢复至正常开工水平预计元宵节后会集中复产。库存方面，受降雪影响，大部分煤矿汽运受限，煤矿库存增加；港口铁路发运量较节日期间有所好转，但仍然处于偏低水平，但港口近期封航频繁，节后北方港口库存快速累积。需求方面，元宵节后下游复工复产进程加快，需求仍有提升可能，短期价格仍易涨难跌。值得关注的是，近期，山西省发布《关于开展煤矿“三超"和隐蔽工作面专项整治的通知》，特别提到煤矿的超能力下达生产经营指标情况、煤矿超能力生产情况（全年原煤产量是否超过核定（设计）生产能力幅度的10%、月度原煤产量是否大于核定（设计）生产能力的10%）、采掘接续紧张情况、布置隐蔽工作面情况等。根据我们测算，2023年山西省煤炭产能约12.1亿吨，当年山西省生产煤炭13.6亿吨，超产1.5亿吨，超产比例12.4%，大于要求的10%，若按照《通知》要求，2024年至少有2.4%的产量压减空间，即山西省至少要减产3000-4000万吨，煤炭特别是炼焦煤供给面临较大收缩。整体上我们认为煤炭供需两端供给最为关键，供给无弹性而需求有弹性，伴随需求的持续增长进而带来供给的压力和供需缺口的劣化，即本轮煤炭产能周期、供给约束带来的高景气周期仍在早中期。基于此，尽管过去三年煤炭板块已有一定涨幅，但尚未充分反映产能周期的底层逻辑以及资源实际价值，而本轮煤炭超额收益也不仅来自于“高股息”策略在熊市中的应用，其根本原因是产能周期下的供需错配带来的上涨，产业逻辑或仍将助推煤炭板块在熊市结束后有不错表现。总体上，能源大通胀背景下，我们认为未来3-5年煤炭供需偏紧的格局仍未改变，优质煤炭企业依然具有高壁垒、高现金、高分红、高股息的属性，叠加煤价筑底推动板块估值重塑，板块投资攻守兼备且具有高性价比，再度提示板块逢低配置。
煤炭板块及个股表现：煤炭板块。
价格跟踪：港口动力煤价格环比上。
截至2月23日，CCTD秦皇岛动力煤（Q5500)综合交易价749.0元/吨，周环比上涨5.0元/吨。环渤海动力煤(Q5500)综合平均价格指数为730.0元/吨，周环比上涨2.0元/吨。截至2月，煤（05500)年度长协价708.0元/吨，月环比下跌2.0元/吨。
港口动力煤：港口动力煤：截至2月23日，秦皇岛港动力煤(Q5500)山西产市场价933.0元/吨，周上涨24.（元/吨。产地动力煤：截至2月23日，陕西榆林动力块煤（Q6000）坑口价985.0元/吨，周环比持平；内蒙古东胜大块精煤车板价（Q5500）753.5元/吨，周环比下跌1.8元/吨；大同南郊粘煤坑口价（含税）（Q5500）765.0元/吨，周环比上涨17.0元/吨。
港口炼焦煤：截至2月22日，京唐港山西产主焦煤库提价(含税)2550.0元/吨，周环比下跌50.0元/吨；连云港山西产主焦煤平仓价(含税)2841.6元/吨，周环比下跌59.2元/吨。产地炼焦煤：截至2月23日，临汾肥精煤车板价(含税)2450.0元/吨，周环比下跌50.0元/吨；充州气精煤车板价1420.0元/吨，周环比持平；邢台1/3焦精煤车板价2150.0元/吨，周环比持平。国际炼焦煤：截至2月23日，澳大利亚峰景煤矿硬焦煤中国到岸价328.5美元/吨，周环比下跌0.6美元/吨。
4、无烟煤及喷吹煤价格。
供需跟踪：电厂煤炭日耗环比上升。
3、煤电日耗及库存情况。
内陆17省：截至2月22日，内陆十七省煤炭库存7400.60万吨，较上周下降519.80万吨，周环比下降6.56%；日耗为404.20万吨，较上周上升21.00万吨/日，周环比增加5.48%；可用天数为18.3天，较上周下降2.40天。
2沿海八省：截至2月22日，沿海八省煤炭库存3301.10万吨，较上周上1日耗为197.60万吨，较上周上升30.00万吨/日，周环比增加17.90%；天。
一截至2月22日，三峡出库流量6830立方米/秒，周环比下降0.73%%。
截至2月22日，沿海八省煤炭库存3301.10万吨，较上周上升220.30万吨，周环比增加7.60万吨，较上周上升30.00万吨/日，周环比增加17.90%；可用天数为16.7天，较上周下降。
26：沿海八省区日均耗煤变化情况（万吨）。
4、下游冶金煤价格及需求。
截至2月23日，Myspic综合钢价指数148.2点，周环比下跌1.47点。截至2月23日，唐山产一级冶金焦价格2560.0元/吨，周环比下跌110.0元/吨。
截至2月23日，Myspic综合钢价指数148.2点，周环比下跌1.47点。
高炉开工率：截至2月23日，全国高炉开工率75.6%，周环比下降0.74百分点。吨焦利润：截至2月23日，独立焦化企业吨焦平均利润为-107元/吨，周环比下降64.0元/吨。高炉吨钢利润：截至2月23日，螺纹钢高炉吨钢利润为-216.23元/吨，周环比增加90.9元/吨电炉吨钢利润：截至2月23日，螺纹钢电炉吨钢利润为-268.27元/吨，周环比下降92.5元/吨高炉废钢消耗比：截至2月23日，纯高炉企业废钢消耗比为15.55%，周环比下降0.1个百分点铁废价差：截至2月22日，铁水废钢价差为-220.7元/吨，周环比下降166.7元/吨。
5、下游化工、建材价格及需求。
?截至2月23日，湖北地区尿素(小颗粒)市场价(平均价)2256.0元/吨，周环比下跌4.0元/吨；广东地区尿素(小颗粒)市场价(平均价)2432.0元/吨，周环比上涨22.0元/吨；东北地区尿素(小颗粒)市场价(平均价)2326.0元/吨，周环比上涨30.0元/吨。
?截至2月23日，全国甲醇价格指数较上周同期下跌28点至2451点。
截至2月23日，全国乙二醇价格指数较上周同期下跌38点至4661点。
截至2月23日，全国合成氨价格指数较上周同期上涨106点至2546点。
截至2月23日，全国醋酸价格指数较上周同期下跌66点至3035点。
2截至2月23日，全国水泥价格指数较上周同期下跌0.17点至106.9点，截至2月23日，水泥熟料产能利用率为31.0%，周环比下跌10.9百分点。截至2月23日，浮法玻璃开工率为85.1%，周环比上涨0.3百分点。截至2月23日，化工周度耗煤为633.62万吨，较上周下降9.15万吨/日，周环比下降1.42百分点，库存情况：秦皇岛港库存环比上升。
秦港库存：截至2月23日，秦皇岛港煤炭库存较上周同期增加97.0万吨至527.0万吨。一55港动力煤库存：截至2月16日，55个港口动力煤库存较上周同期下降77.8万吨至5189.5万吨。产地库存：截至2月23日，462家样本矿山动力煤库存193.2万吨，上周周度日均发运量149.8万吨，周环比上涨43.4万吨。
.2月23日，波罗的海干散货指数(BDI)为1866.0点，周环比上涨256.0点；截至2月23日，输综合运价指数（CCSFI)为723.2点，周环比上涨20.6点。
.截至2月22日周四，本周大秦线煤炭周度日均发运量103.4万吨，上周周度日均发运量90.3万吨，周环比上涨13.1万吨。
截至2月16日周五，本周中国铁路煤炭发货量3527.0万吨，上周周度日均发运量3400.7万吨，周环比上涨126.3万吨。
环渤海四大港口货船比情况。
截至2月23日，环渤海地区四大港口（秦皇岛港、黄驿港、曹妃甸港、京唐港东港）的库（周环比增加52.00万吨），锚地船舶数为73.0艘（周环比下降27.00艘），货船比（库存0，周环比增加3.29。
?未来十天全国大部地区气温偏低南方地区多阴雨天气。黄淮南部、江汉、江淮、江南北部和西部、华南中西部及贵州东部、重庆、西藏东南部等地累计降水量有15～30毫米，部分地区40～70毫米；西北地区、华北西部和北部、东北地区大部、黄淮北部累计降水量有3～8毫米，青海东南部、甘肃南部、陕西南部等地的部分地区有10～20毫米；上述大部地区降水量较常年同期偏多4～7成，局地偏多1倍以上。
未来11-14天（3月5-8日），江淮、江汉、江南、华南及贵州、西藏东南部等地累计降水量有5～30毫米；西北地区东部、黄淮西部累计降水量有3～8毫米，我国其余地区降水量一般不足3毫米或无降水。
【潞安环能】潞安环能2024年1月主要运营数据公告：路安环能2024年1月原煤产量453吨，2023年1月原煤产量496万吨，同比下降8.67%。2024年1月商品煤销量432万吨，2023年1月商品煤销量405万吨，同比上升6.67%。
【安源煤业】安源煤业关于所属丰城区域山西煤矿和流舍煤矿复产的公告：山西煤矿和流舍煤矿两对矿井在停产期内，完成了停产整改相关工作。经公司按相关规定组织复产验收，矿并具备恢复生产条件，于2024年2月19日恢复正常生产。上述两对煤矿本次停产期间为2024年1月27日至2024年2月18日，实际停产天数为23天；本次停产预计影响公司商品煤产量2.6万吨，预计损失633万元左右。公司后期将通过进一步优化生产方案等措施，最大限度挽回经济损失。敬请广大投资者注意投资风险。
【充矿能源】充矿能源集团股份有限公司关于回购注销部分限制性股票通知债权人的公告：充矿能源集团股份有限公司（“公司”“本公司”）于2024年2月23日召开第九届董事会第五次会议和第九届监事会第四次会议，审议批准了《关于回购注销部分激励对象限制性股票的议案》，同意根据2021年A股限制性股票激励计划回购22名激励对象已获授但尚未解除限售的限制性股票140.118万股。
        """

    ]

    sentences = sc.cut(paragraph[0])

    print('number of sentences:', len(sentences))
    for sentence in sentences:
        print('----------------')
        print(sentence)

    # paragraph_cutter = ParagraphCutter()
    # paragraph = paragraph_cutter.force_segment(sentences,500)
    # for item in paragraph:
    #     print(item)
    #     print(len(item))