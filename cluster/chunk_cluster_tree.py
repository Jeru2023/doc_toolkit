from sentence_splitter.sentence_cutter import SentenceCutter
from cluster.topic_cluster import TopicCluster


class Cluster2Node(SentenceCutter):
    """
    定义节点类
    """
    def __init__(self, index, left=None, right=None):
        self.index: int = index  # 节点索引
        self.left = left  # 左子节点
        self.right = right  # 右子节点
        # 节点基本信息
        self.word_cnt: int = 0  # 此节点下所有叶子节点的段落长度和
        self.leafs = []  # 存储节点下包含的所有叶子链接
        # 叶节点特有信息
        self.data = None

    def __repr__(self):
        return f"Node(index={self.index}, word_cnt={self.word_cnt})"


class Cluster2Tree:
    """
    二分链表树
    """

    def __init__(self):
        self.topic_cluster = TopicCluster()

    @staticmethod
    def paragraphs2docs(paragraphs):
        """将paragraphs转换为docs格式，用于聚类入参"""
        # paragraphs.sort(key=lambda x: x['index'])
        docs = [''.join([sentence['text'] for sentence in paragraph['sentences']]) for paragraph in paragraphs]
        return docs

    def build_cluster_tree(self, paragraphs, chunk_size=2000):
        """
        构建链表: a -> b, c
        [[ 0,  1,  0.2,  2,]
         [ 2,  3,  0.5,  2,]
         [ 4,  5,  0.8,  4,]]
        """
        paragraphs.sort(key=lambda x: x['index'])
        docs = self.paragraphs2docs(paragraphs)
        linkage_matrix = self.topic_cluster.cluster(docs)
        node_a_index = node_cnt = len(linkage_matrix) + 1  # 初始化非叶节点索引
        nodes_dict = {}  # 临时存储节点列表，到root节点时，只有一个元素

        for row in linkage_matrix:
            # 分支节点
            if (node_b := int(row[0])) < node_cnt:  # 叶子节点
                left_node = Cluster2Node(node_b)
                left_node.word_cnt = len(docs[node_b])
                left_node.leafs = [left_node]
                left_node.data = paragraphs[node_b]
            else:
                left_node = nodes_dict[node_b]
                nodes_dict.pop(node_b)
            if (node_c := int(row[1])) < node_cnt:  # 叶子节点
                right_node = Cluster2Node(node_c)
                right_node.word_cnt = len(docs[node_c])
                right_node.leafs = [right_node]
                right_node.data = paragraphs[node_c]
            else:
                right_node = nodes_dict[node_c]
                nodes_dict.pop(node_c)

            # 创建父节点
            node_a = Cluster2Node(
                node_a_index,
                left=left_node,
                right=right_node,
            )
            node_a.word_cnt = left_node.word_cnt + right_node.word_cnt
            node_a.leafs = left_node.leafs + right_node.leafs
            node_a.leafs.sort(key=lambda x: x.index)

            node_a_index += 1  # 下一个父节点index+1
            nodes_dict.update({node_a.index: node_a})

        # 聚类树root生成
        root = nodes_dict.popitem()[1]

        return [{
            'indexs': [node['index'] for node in chunk],
            'paragraphs': chunk}
            for chunk in self.cut(root, chunk_size=chunk_size)]

    def cut(self, branch, chunk_size=2000):
        """
        从任一节点递归遍历，做2000字内切分
        """
        if branch.word_cnt <= chunk_size or len(branch.leafs) <= 1:
            return [[node.data for node in branch.leafs]]
        return self.cut(branch.left) + self.cut(branch.right)


if __name__ == '__main__':

    paragraphs = [{'index': 0, 'sentences': [{'entity_subject': None, 'coref_subject': None, 'entities': [{'产品名': {'锂电池': 1, '动力电池': 1}}], 'text': '在动力电池及电化学储能领域，锂电池主要的技术进步来源于结构创新和材料创新，前者是在物理层面对“电芯—模组—电池包”进行结构优化，达到兼顾提高电池包体积比能量密度与降低成本的目的，后者是在化学层面对电池材料进行探索，达到兼顾提高单体电池性能与降低成本的目的。'}]}, {'index': 1, 'sentences': [{'entity_subject': None, 'coref_subject': None, 'entities': [{'产品名': {'锂离子电池': 1, '电池模组': 1}}, {'技术名': {'高压元器件': 1, '管理系统': 1}}], 'text': '锂离子电池传统的应用形式包括“电芯—模组—电池包”三层结构，电池模组在电池包箱体内排列，辅以管理系统和高压元器件，组成完整的电池包。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'产品名': {'电池': 1}}], 'text': '目前电池结构创新主要朝无模组化方向发展，减少零件数量降低成本，同时节约空间提高体积比能量密度。'}]}, {'index': 2, 'sentences': [{'entity_subject': None, 'coref_subject': None, 'entities': [{'技术名': {'电池结构': 1, '电池连接系统': 1, 'CTP': 1}}], 'text': '作为电芯之间串并联以及采集温度和电压等信号的连接传输组件，电池连接系统伴随电池结构创新不断迭代升级，主要体现在信号线路发展、集成工艺多样化以及CTP/CTC 趋势下产品尺寸增加等方面。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'产品名': {'锂离子电池': 1, '动力电池': 1}}, {'技术名': {'铜线线束': 1}}], 'text': '具体如下：①信号线路发展早期锂离子电池主要采用铜线线束作为信号线路，常规线束由铜线外部包围塑料而成，连接电池包时每一根线束到达一个电极，当动力电池包电流信号较多时，则需要多根线束配合使用，对空间挤占较大。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [], 'text': '在电池包装配环节由于线束较多、组装较为复杂，且需要依赖人工将端口固定到电池包上，导致装配自动化程度较低。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'产品名': {'铜线线束': 1, 'FPC': 1}}], 'text': '相较铜线线束，FPC 由于其高度集成、厚度较薄、柔软度较高等优点，在安全性、轻量化、布局规整等方面具备突出优势，装配时可通过机械手臂抓取直接放置电池包上、自动化程度高，适合规模化大批量生产。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'产品名': {'动力电池连接系统': 2, 'FPC': 4}}, {'行业名': {'新能源汽车': 1}}, {'时间': {'2017 年': 1}}], 'text': '2017 年前后，FPC 开始小批量应用于新能源汽车动力电池连接系统，随着 FPC 展现出的优异性能以及规模化生产后快速降本，FPC 替代传统线束的进程明显提速，目前 FPC 已经成为动力电池连接系统的主要选择。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'产品名': {'FFC': 2, 'FPC': 1}}, {'技术名': {'绝缘材料': 1, '多股铜丝绞合导体': 1}}], 'text': 'FFC 为采用绝缘材料包裹多股铜丝绞合导体压合而成的扁平型电缆，相较FPC 具有成本低廉、强度高的优点，但由于 FFC 作为信号采集线路使用时存在加工难度较高的问题，目前在电池连接系统中尚未规模应用。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'产品名': {'FFC': 1}}], 'text': '未来，随着 FFC在电池连接系统中应用技术的不断成熟，其有望凭借低成本、高强度的优势成为动力电池连接系统的主要选择之一。'}]}, {'index': 3, 'sentences': [{'entity_subject': None, 'coref_subject': None, 'entities': [{'产品名': {'铜铝排': 1, '注塑托盘': 1, '绝缘膜热压 CCS': 1}}, {'技术名': {'热铆': 1}}], 'text': '②集成工艺多样化发展在公司推出绝缘膜热压 CCS 前，行业内主要采用注塑托盘的集成方案，通过热铆或卡扣固定托盘、信号线路及铜铝排。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'产品名': {'电池': 1}}], 'text': '由于塑胶结构件较厚且重量相对较重，注塑托盘方案一定程度上影响电池成组效率与空间利用率。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'产品名': {'注塑托盘': 1, '绝缘膜热压 CCS': 1, '绝缘膜': 1}}, {'技术名': {'热压工艺': 1}}], 'text': '绝缘膜热压 CCS通过热压工艺将绝缘膜与信号线路、铝巴压合为一块薄片，与注塑托盘相比具有重量轻、空间利用率高、结构简单等优点，契合下游提升电池包成组效率和空间利用率的发展趋势，适合大尺寸产品应用。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'产品名': {'吸塑盘': 2, '注塑托盘': 1}}], 'text': '近年来还出现了吸塑盘方案，采用较为轻薄的吸塑盘替代注塑托盘，也能有效降低重量、提高空间利用率。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'技术名': {'电池结构': 1, '电池连接系统': 1}}], 'text': '③动力电池 CTP/CTC发展使得电池连接系统尺寸不断增加动力电池厂商和车企在电池结构方面的研发创新始终围绕着成组效率和空间利用率提升开展，致力于达到提升能量密度、降低成本的目的。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [], 'text': '过去几年，电池包结构创新主要体现在通过增加标准化电池模组尺寸、减少模组数量等，提升电池包的空间利用率和系统能量密度，如从 355模组向 590模组、大尺寸模组演化。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'产品名': {'动力电池包': 1, '模组': 1}}, {'技术名': {'CTP': 1}}], 'text': '由于模组的存在降低了动力电池包的空间利用率，影响成组效率，目前主流电池厂商已逐步采用 CTP 高效成组技术，跳过标准化模组环节，将电芯直接集成至电池包，突破传统“电芯—模组—电池包”三层结构。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'公司名': {'宁德时代': 2}}, {'产品名': {'电池': 1}}, {'技术名': {'CTP': 1}}, {'地点': {'宁德': 1}}], 'text': '根据宁德时代官方网站，以宁德时代 CTP 技术为例，通过简化模组结构，能够使电池包空间利用率提高20%~30%，零部件数量减少 40%，生产效率提升50%。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'技术名': {'CTC 技术': 1, 'CTP': 1}}, {'行业名': {'新能源汽车': 1}}], 'text': '在CTP 基础上，行业内部分电池厂家、车企已开始布局 CTC 技术，将电芯直接集成至汽车底盘，可省去模组、打包过程，实现更高程度集成化，进一步提升新能源汽车续航里程。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [], 'text': '上述大模组或 CTP/CTC 发展趋势对电池连接系统设计、生产制造工艺水平均提出了更高的需求，电池连接系统尺寸需相应增加，同时进一步提升集成化水平，简化结构的同时提高空间利用率，以适应电池成组技术发展需求。'}]}, {'index': 4, 'sentences': [{'entity_subject': None, 'coref_subject': None, 'entities': [{'行业名': {'新能源汽车': 2}}], 'text': '公司下游行业包括新能源汽车、电化学储能、新能源发电、轨道交通等，近年来公司下游行业相关市场需求保持了稳定增长，部分行业如新能源汽车、电化学储能正处于高速发展阶段，为公司实现业务增长提供了有利的市场环境。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'行业名': {'汽车行业': 1}}], 'text': '相关行业市场需求情况概况如下：中国作为世界最大的汽车消费市场和生产基地，对全球汽车行业的发展起到关键性作用。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'行业名': {'汽车产业': 1}}], 'text': '汽车产业是国民经济的重要支柱产业，在国民经济和社会发展中发挥着重要作用。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'行业名': {'新能源汽车': 1, '汽车行业': 1}}], 'text': '新能源汽车作为我国的战略新兴产业，是我国汽车行业实现弯道超车的重要契机。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'公司名': {'工信部': 1, '财政部': 1}}, {'行业名': {'新能源汽车': 1, '新能源汽车产业': 1}}, {'时间': {'2013 年': 1}}], 'text': '自 2013 年以来，国家发改委、财政部、工信部以及科技部等部门陆续出台了一系列鼓励和推广新能源汽车发展的政策，对我国新能源汽车产业的快速成长发挥了重要的促进作用。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'行业名': {'新能源汽车行业': 1}}, {'时间': {'2035 年': 1}}], 'text': '在国家“十四五”规划和 2035 年远景目标纲要中，新能源汽车行业被列为战略性新兴产业之一。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'行业名': {'新能源汽车行业': 1}}], 'text': '在政策、需求、技术等多重因素驱动下，新能源汽车行业正处于高速发展的黄金时期。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'行业名': {'新能源汽车': 1}}], 'text': '①中国新能源汽车市场情况在国家政策扶持和技术进步的推动下，我国新能源汽车的产业规模正在逐渐扩大，处于行业的高速发展期。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'产品名': {'中国新能源汽车': 1}}, {'时间': {'2022 年 1-6 月': 1, '2023年 1-6月': 1, '2022年1-6月': 1}}], 'text': '根据中国汽车工业协会的数据显示，2023年 1-6月中国新能源汽车产量为 378.70万辆，较 2022年1-6月增加了113.36万辆，同比增长 42.72%；销量为 374.47 万辆，较 2022 年 1-6 月增加了 115.28 万辆，同比增长44.48%，产销量均实现大幅增长。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'行业名': {'新能源汽车': 1, '汽车产业': 1, '中国新能源汽车': 1, '汽车': 1, '能源': 1, '信息通信': 1, '交通': 1}}, {'时间': {'2017年~2023年6月': 1}}], 'text': '图：2017年~2023年6月中国新能源汽车产量和销量情况（万辆）数据来源：中国汽车工业协会②全球新能源汽车市场情况当前，全球新一轮科技革命和产业变革蓬勃发展，汽车与能源、交通、信息通信等领域有关技术加速融合，电动化、网联化、智能化成为汽车产业的发展潮流和趋势。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'行业名': {'新能源汽车': 1, '汽车大国': 1, '汽车产业': 1}}], 'text': '近年来，世界主要汽车大国纷纷加强战略谋划、强化政策支持，跨国汽车企业加大研发投入、完善产业布局，新能源汽车已成为全球汽车产业转型发展的主要方向和促进世界经济持续增长的重要引擎。'}]}, {'index': 5, 'sentences': [{'entity_subject': None, 'coref_subject': None, 'entities': [], 'text': '欧洲市场方面，随着碳排放标准不断提高，车企不断加大新能源汽车投入。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'时间': {'二十世纪九十年代': 1, '2014 年': 1}}], 'text': '从二十世纪九十年代开始实施的 EURO 1 排放标准到 2014 年实施的EURO 6 标准，每一代标准都在不断提升对汽车各类排放物的限制，使得车企为了达到排放要求不断加大对新能源汽车的投入。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'行业名': {'新能源汽车': 2}}, {'时间': {'2020 年': 1}}], 'text': '同时，欧洲各国纷纷出台各式新能源汽车政策补贴，自2020 年以来，补贴力度不断加大，欧洲新能源汽车呈现爆发式增长。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'产品名': {'燃油轿车': 1, '小货车': 1}}, {'时间': {'2035年': 1}}], 'text': '洲新售燃油轿车和小货车零排放协议，意味着由汽油、柴油等化石燃料驱动的车型从2035年起将无法在欧盟上市。'}]}, {'index': 6, 'sentences': [{'entity_subject': None, 'coref_subject': None, 'entities': [{'行业名': {'新能源汽车': 1}}, {'时间': {'2019-2020年': 1, '2018年': 1}}], 'text': '美国市场方面，由于特朗普总统取消了奥巴马执政时期的新能源汽车补贴政策，导致2019-2020年美国新能源汽车销量仅为 32万和 32.4万辆，均低于2018年的 35.6 万辆，新能源汽车渗透率仅为 1.5%左右。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'行业名': {'新能源汽车': 2, '新能源': 1}}], 'text': '拜登上任后启动了新能源新政，提出了鼓励新能源汽车的系列政策，包括消费补贴、税收抵免、充电设备建设、公共交通电动化等，美国市场新能源汽车销量逐步提升。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'行业名': {'新能源汽车': 3, '燃油车': 2}}], 'text': '③新能源汽车市场前景广阔与燃油车相比，新能源汽车的能源补充成本更低并且享有利好政策和补贴，这吸引了越来越多的消费者从燃油车转向新能源汽车，带动了行业的市场需求。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'技术名': {'电池技术': 1}}, {'行业名': {'新能源汽车': 2, '汽车': 1}}], 'text': '同时，电池技术的不断发展促使新能源汽车的电池续航里程及充电效率明显提升，智能物联则进一步强化了新能源汽车作为智能技术载体的特征，为汽车革命带来了全新的发展机遇。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'行业名': {'新能源汽车': 1}}], 'text': '此外，在全国范围内扩大充电基础设施的覆盖范围，很大程度上提高了新能源汽车消费者的驾驶体验，降低了里程焦虑。'}]}, {'index': 7, 'sentences': [{'entity_subject': None, 'coref_subject': None, 'entities': [{'行业名': {'新能源汽车': 2, '燃油车': 1}}], 'text': '随着越来越多的消费者关注并且接受新能源汽车，新能源汽车对传统燃油车的替代是顺应行业和国家发展的大趋势。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'行业名': {'新能源汽车行业': 1}}], 'text': '经过多来的市场教育和产业链培育，新能源汽车行业各个环节逐步成熟，丰富和多元化的新能源汽车产品不断满足市场需求，使用环境也在逐步优化和改进，新能源汽车受消费者认可度持续提高。'}]}, {'index': 8, 'sentences': [{'entity_subject': None, 'coref_subject': None, 'entities': [{'产品名': {'新能源汽车': 1}}, {'时间': {'2023 年 1-6 月': 1, '2017 年至 2023 年 6 月': 1}}], 'text': '根据中国汽车工业协会的数据，2017 年至 2023 年 6 月，我国新能源汽车产销量及渗透率不断上升，2023 年 1-6 月新能源汽车产量为 378.70万辆，销量为 374.47万辆，渗透率分别为 28.61%、28.29%。'}]}, {'index': 9, 'sentences': [{'entity_subject': None, 'coref_subject': None, 'entities': [{'产品名': {'风电': 1, '光伏': 1}}, {'时间': {'2017年~2023年6月': 2}}], 'text': '图：2017年~2023年6月我国汽车总产量及新能源汽车产量（月度）单位：辆数据来源：中国汽车工业协会图：2017年~2023年6月我国汽车总销量及新能源汽车销量（月度）单位：辆数据来源：中国汽车工业协会随着相关政策不断向清洁能源倾斜，光伏、风电等可再生能源发电占比快速提升，但是可再生能源具有不连续、不稳定、不可控的特性，因此需要大规模储能技术参与调节。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'行业名': {'储能': 1, '新型储能': 1}}], 'text': '在政策及市场需求共同刺激下，储能市场需求预计将持续增长，进而推动新型储能快速发展。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'行业名': {'新型储能': 1}}], 'text': '新型储能主要场景为电化学储能。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'产品名': {'锂电池储能': 1, '电化学储能': 1}}], 'text': '与传统机械储能相比，电化学储能不受自然条件影响，特别是锂电池储能，具有充电速度快、放电功率大、系统效率高、建设周期短等优点，可以灵活运用于电力系统各环节及其他各类场景中。'}]}, {'index': 10, 'sentences': [{'entity_subject': None, 'coref_subject': None, 'entities': [{'时间': {'2030 年': 1, '2025 年': 1, '2021年 7 月 15 日': 1}}], 'text': '2021年 7 月 15 日，国家发展改革委、国家能源局联合发布《关于加快推动新型储能发展的指导意见》提出 2025 年实现新型储能从商业化初期向规模化发展转变、新型储能装机规模达 30GW 以上，2030 年实现新型储能全面市场化发展。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'时间': {'2022年1月29日': 1}}], 'text': '2022年1月29日，国家发展改革委、国家能源局联合发布《“十四五”新型储能发展实施方案》，进一步指出要支撑构建新型电力系统，加快推动新型储能高质量规模化发展。'}]}, {'index': 11, 'sentences': [{'entity_subject': None, 'coref_subject': None, 'entities': [{'时间': {'2022 年': 1, '2016 年': 1}}, {'地点': {'中国': 1}}], 'text': '根据 CNESA 的统计，全球新型储能项目新增装机规模由 2016 年的 0.6GW增加至 2022 年的 20.4GW，年均复合增速接近 80%；其中中国新型储能新增装机规模由0.1GW 增加至7.3GW，年均复合增速超过 100%。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'时间': {'2022年': 1}}], 'text': '至2022年末，全球电力系统中已投运新型储能项目累计装机规模达45.7GW，中国已累计达13.1GW。'}]}, {'index': 12, 'sentences': [{'entity_subject': None, 'coref_subject': None, 'entities': [{'产品名': {'锂电池': 1}}, {'技术名': {'新型储能技术': 1}}, {'行业名': {'可再生能源': 1}}], 'text': '随着可再生能源装机规模的持续增长、储能及电价相关政策的不断完善，以锂电池为主的新型储能技术有望在相关机制的推动下迎来高速发展契机。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'时间': {'2020-2025年': 1, '2025 年': 1}}], 'text': '国家发改委、能源局发布的《关于加快推动新型储能发展的指导意见》明确了 2025 年新型储能装机规模达 30GW 以上的目标，以此计算，2020-2025年均复合增长率将超50%。'}]}, {'index': 13, 'sentences': [{'entity_subject': None, 'coref_subject': None, 'entities': [], 'text': '在环境问题日益严重的背景下，为了实现“碳达峰”'}]}, {'index': 14, 'sentences': [{'entity_subject': None, 'coref_subject': None, 'entities': [{'行业名': {'新能源': 1, '清洁能源': 1}}], 'text': '“碳中和”的目标和社会的可持续发展，发展清洁能源已经成为世界范围内应对生态环境问题的共同选择，其中光伏、风电作为新能源发电重要方式未来有着较大发展潜力。'}]}, {'index': 15, 'sentences': [{'entity_subject': None, 'coref_subject': None, 'entities': [{'时间': {'2022年': 1}}], 'text': '①光伏市场发展情况根据21世纪可再生能源政策网络及中国光伏行业协会数据，2022年，全球光伏市场新增装机量为 230GW，同比增长 31.43%，全球累计光伏发电装机总量达到了 1,156GW，同比增长 22.72%。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'行业名': {'光伏发电': 2}}, {'时间': {'2017 年至 2022 年': 1}}], 'text': '2017 年至 2022 年，全球光伏发电新增装机量年复合增长率为18.36%，光伏发电累计装机量年复合增长率达到了23.52%，均保持了较高的增长速率。'}]}, {'index': 16, 'sentences': [{'entity_subject': None, 'coref_subject': None, 'entities': [{'时间': {'2017~2022年': 1, '2022年': 1}}], 'text': '图：2017~2022年全球光伏新增和累计装机容量数据来源：21世纪可再生能源政策网络、WIND、中国光伏行业协会根据国家能源局及 21世纪可再生能源政策网络数据，2022年，中国光伏市场新增装机量为 87.41GW，同比增长 56.09%，累计光伏发电装机总量达到了计装机容量连续 6年位居世界第一，累计装机容量年复合增长率达到 24.55%。'}]}, {'index': 17, 'sentences': [{'entity_subject': None, 'coref_subject': None, 'entities': [{'时间': {'2017—2022年': 1, '2025 年': 1}}], 'text': '图：2017—2022年我国光伏电站和累计装机容量数据来源：国家能源局、21世纪可再生能源政策网络数据、WIND根据中国光伏行业协会测算，在十四五“碳中和”政策支持下，2025 年国内光伏新增装机预计可达 90-110GW，继续保持全球领先的位置。'}]}, {'index': 18, 'sentences': [{'entity_subject': None, 'coref_subject': None, 'entities': [{'行业名': {'风电市场': 1}}, {'时间': {'2022 年': 1}}], 'text': '②风电市场发展情况根据全球风能协会统计数据，2022 年全球风电市场新增装机容量 77.59GW，累计装机容量 906.22GW，累计装机容量同比增长 9.27%。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'产品名': {'风电': 1}}, {'时间': {'2017 至 2022 年': 1}}], 'text': '2017 至 2022 年，风电累计装机容量从 540.43GW 增长至 906.22GW，年复合增长率达 10.89%。'}]}, {'index': 19, 'sentences': [{'entity_subject': None, 'coref_subject': None, 'entities': [{'时间': {'2017~2022年': 1, '2017 年': 1}}], 'text': '图：2017~2022年全球新增和累计风电装机容量单位：GW数据来源：全球风能协会、WIND根据国家能源局统计数据，2017 年以来，中国风电装机规模保持增长态势，累计装机容量年复合增长率达 17.42%。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'时间': {'2022 年': 1}}], 'text': '2022 年全国新增装机容量 37.63GW，累计装机容量365.4GW，累计装机容量同比增长 11.24%。'}]}, {'index': 20, 'sentences': [{'entity_subject': None, 'coref_subject': None, 'entities': [{'公司名': {'海上风电': 1}}, {'时间': {'2017年-2022年': 1, '2025年': 2, '2021-2025年': 1, '2022-2025年': 1}}], 'text': '图：2017年-2022年中国新增和累计风电装机容量单位：GW数据来源：国家能源局根据GWEC保守预测，我国2025年陆上风电新增装机容量有望达到45GW，2021-2025年CAGR达到10.67%；海上风电2025年新增装机容量有望达到5GW，2022-2025年 CAGR 达到7.72%。'}]}, {'index': 21, 'sentences': [{'entity_subject': None, 'coref_subject': None, 'entities': [{'时间': {'2016年': 1, '2015 年': 1, '2025 年': 1, '2004 年': 1}}], 'text': '①高速铁路建设方兴未艾我国高铁建设有两波浪潮，第一波是 2004 年《中长期铁路网规划》确定规划建设“四纵四横”200 公里/小时客运专线，至 2015 年底，全国铁路营业里程达到12.1万公里，其中高速铁路 1.9 万公里，跨区域快速通道基本形成；第二波开始于2016年修编新的《中长期铁路网规划》，在“四纵四横”高速铁路基础上，于 2025 年形成以“八纵八横”主通道为骨架、区域连接线衔接、城际铁路补充的高速铁路网。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'时间': {'2030 年': 1}}], 'text': '展望至 2030 年实现省会城市高速铁路通达、区际之间高效便捷相连。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'产品名': {'动车组': 1}}], 'text': '目前我国正处于第二波高铁建设浪潮中期，高快速铁路建设将拉动动车组车辆保有量进一步扩大。'}]}, {'index': 22, 'sentences': [{'entity_subject': None, 'coref_subject': None, 'entities': [{'时间': {'2025年': 1, '5-10 年': 1, '2025 年': 1, '2008-2018年': 1}}, {'地点': {'中国': 1}}], 'text': '图：2008-2018年中国“四纵四横”高速铁路逐步形成资料来源：央视网、国家铁路局、UIC图：计划于2025年形成的“八纵八横”高速铁路网资料来源：央视网、国家铁路局、UIC根据《中长期铁路网规划》，到 2025 年铁路网规模达到 17.5 万公里左右，其中高速铁路 3.8 万公里左右（不包括城际快速铁路），根据《规划》中未建成的干线高速铁路和支线快速铁路计算，未来 5-10 年将新建通车高速铁路（包括城际快速铁路）23,000 公里以上。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'公司名': {'复兴号': 1}}, {'时间': {'5-10 年': 1}}], 'text': '展望未来 5-10 年，复兴号总订单规模有望超4,000标准组（列），约合 5,000亿元市场规模，年均 500-1,000亿元，不低于“和谐号”时代水平。'}]}, {'index': 23, 'sentences': [{'entity_subject': None, 'coref_subject': None, 'entities': [{'行业名': {'城市轨道交通': 2}}], 'text': '②城市轨道交通进入黄金发展期随着中国城市化进程的推进，城市轨道交通进入黄金发展期。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'时间': {'2022 年': 1}}], 'text': '根据中国城市轨道交通协会的数据，2022 年全年共完成建设投资 5,443.97 亿元，在建线路总长6,350.55千米。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'产品名': {'电池': 1}}, {'行业名': {'城市轨道交通': 1}}], 'text': '图：近年来我国城市轨道交通在建线路总长单位：公里数据来源：中国城市轨道交通协会政策及市场双重驱动行业发展，带动电池连接市场需求高速增长。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'行业名': {'汽车': 1, '新能源汽车': 2, '汽车产业': 1}}], 'text': '①产业政策的大力支持有利于行业快速发展近年来，世界主要汽车大国纷纷加强对新能源汽车政策支持，新能源汽车已成为全球汽车产业转型发展的主要方向和促进世界经济持续增长的重要引擎。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'产品名': {'电池': 1}}, {'行业名': {'新能源汽车行业': 1}}], 'text': '受行业政策及市场需求双重驱动，全球新能源汽车行业进入快速增长阶段，为电池连接系统带来巨大需求空间，并推动产品形态、功能不断发展。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'行业名': {'可再生能源': 1, '新能源汽车': 1}}], 'text': '以我国为例，新能源汽车、可再生能源作为重点发展的战略性、基础性支柱产业，国家层面出台了多项政策促进上述产业发展，具体产业政策详见本节“二、发行人所处行业的基本情况和竞争状况”之'}]}, {'index': 24, 'sentences': [{'entity_subject': None, 'coref_subject': None, 'entities': [], 'text': '“（二）行业主管部门、行业监管体制、行业主要法律法规政策及对发行人的主要影响”之'}]}, {'index': 25, 'sentences': [{'entity_subject': None, 'coref_subject': None, 'entities': [], 'text': '“2、行业主要法律法规及政策”。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'行业名': {'电连接行业': 1}}], 'text': '产业政策的大力支持为电连接行业提供了广阔的发展空间，有利于行业快速发展。'}]}, {'index': 26, 'sentences': [{'entity_subject': None, 'coref_subject': None, 'entities': [{'行业名': {'电连接行业': 2, '新能源汽车': 1}}], 'text': '②电连接行业下游应用多元化、新兴领域市场需求高速发展电连接行业的下游应用领域十分广泛，包括新能源汽车、电化学储能、轨道交通、工业变频、新能源发电等领域。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'行业名': {'新兴领域': 1, '电化学储能': 1, '新能源汽车': 1}}], 'text': '近年来，随着技术进步，新能源汽车、电化学储能等新兴领域市场需求高速发展，为电连接行业的发展及应用提供了更加广阔的平台与保障。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'产品名': {'驱动电机': 1, '动力电池': 1}}, {'行业名': {'新能源汽车市场': 1, '新能源汽车': 1}}], 'text': '以新能源汽车为例，随着动力电池、驱动电机等关键技术取得突破，市场竞争力明显增强，新能源汽车市场渗透率水平不断提升。'}]}, {'index': 27, 'sentences': [{'entity_subject': None, 'coref_subject': None, 'entities': [{'行业名': {'电连接行业': 1}}], 'text': '①人才匮乏，制约了行业的发展电连接行业不仅需要专业的生产技术人才、管理人才，还需要大量产品研发人才，尤其需要熟悉生产工艺与产品研发的复合型人才。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [], 'text': '随着行业规模的增加以及下游需求的多样化、专业化，对行业技术的要求越来越高，行业发展需要大量的专业技术人才作为支持。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [], 'text': '但由于国内目前在此领域的高端技术人才较为匮乏，尤其是复合型人才相对缺乏，行业发展在一定程度上受到限制。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'行业名': {'新能源汽车行业': 2}}, {'时间': {'2021 年': 1}}], 'text': '②新能源汽车行业竞争格局尚不稳定我国新能源汽车行业经过十余年发展，尽管已从早期的政策驱动开始逐步转变为市场驱动，2021 年以来行业保持较高景气度水平，但行业尚处于发展早期阶段，行业竞争格局尚不稳定。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'公司名': {'华为': 1, '苹果': 1, '小米': 1, '百度': 1}}, {'行业名': {'新能源汽车': 1}}], 'text': '由于新能源汽车风口正盛，除造车新势力以及传统整车厂外，科技巨头如苹果、小米、华为、百度等纷纷开始跨界造车，抢占蓝海市场。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'行业名': {'新能源汽车': 1}}], 'text': '未来行业增长一旦放缓、行业竞争加剧，可能会出现部分新能源汽车厂家被淘汰，导致行业竞争格局发生变化，不利于上下游行业稳定发展。'}, {'entity_subject': None, 'coref_subject': '公司', 'entities': [{'行业名': {'新能源汽车': 1}}], 'text': '公司所处行业的发展与下游新能源汽车、电化学储能、轨道交通、工业变频、新能源发电等行业的发展状况息息相关，行业发展的周期性主要受下游市场需求影响。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'行业名': {'新能源行业': 1}}], 'text': '随着我国“碳达峰”、“碳中和”目标的提出，新能源行业迎来了新一轮的增长高峰期，相关需求持续增加。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'行业名': {'新能源汽车': 1, '新能源行业': 1}}], 'text': '目前我国新能源行业仍处于行业发展周期中的成长阶段，新能源汽车、电化学储能等相关行业仍处于行业的上升期。'}]}, {'index': 28, 'sentences': [{'entity_subject': None, 'coref_subject': None, 'entities': [{'行业名': {'轨道交通': 1, '工业变频': 1}}], 'text': '在轨道交通、工业变频等领域，需求主要受社会经济发展水平、经济周期波动等因素影响，与宏观经济发展周期具有一定相关性。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'行业名': {'新能源汽车': 1}}], 'text': '面临机遇与风险、行业周期性特征在报告期内的变化和未来可预见的变化趋势公司产品的下游应用领域包括新能源汽车、电化学储能、轨道交通、工业变频、新能源发电等，由于各应用领域所处发展阶段不同，导致上游细分行业技术水平、行业发展态势等存在一定差异。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'产品名': {'电控母排': 1, '电化学储能': 1, '电池连接系统': 1}}, {'行业名': {'新能源汽车': 1}}], 'text': '新能源汽车、电化学储能的市场规模与技术水平均处于快速发展阶段，对电池连接系统、电控母排等上游配套产品需求规模快速增加，对产品轻量化、集成化要求不断提升，上游细分行业内主要企业相应处于快速占领市场份额的阶段，行业进入门槛不断提升。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'产品名': {'电控母排': 1, '电池连接系统': 1}}], 'text': '未来随着行业整体技术实力的提升、国家产业政策的支持以及下游行业需求的增长，预计短期内电池连接系统、电控母排等产品市场需求仍将保持较快增长。'}]}, {'index': 29, 'sentences': [{'entity_subject': None, 'coref_subject': None, 'entities': [{'行业名': {'轨道交通': 1, '新能源发电': 1}}], 'text': '轨道交通、工业变频、新能源发电等领域竞争格局较为稳定，报告期内上游工业电气母排细分行业技术水平及特点、进入本行业主要壁垒、行业发展态势、面临机遇与风险、行业周期性特征等未发生重大变化，预计未来亦不会发生重大变化。'}]}, {'index': 30, 'sentences': [{'entity_subject': None, 'coref_subject': None, 'entities': [{'产品名': {'镍氢电池': 1, '新能源电池': 1, '锂离子电池': 1, '铅酸电池': 1}}, {'行业名': {'新能源电池': 1}}], 'text': '近年来，新能源电池技术发展迅速，由最早的铅酸电池到镍氢电池，再到如今的锂离子电池，技术路径变化较大。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'产品名': {'新能源电池': 1}}, {'行业名': {'新能源电池': 1}}], 'text': '现阶段新能源电池技术路线仍然处于不断发展的过程中，技术路线发展方向包括材料创新和结构创新。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'产品名': {'三元锂电池': 1, '钴酸锂电池': 1, '氢燃料电池': 1, '锰酸锂电池': 1, '磷酸铁锂电池': 1, '固态锂离子电池': 1, '钠离子电池': 1}}], 'text': '材料创新属于化学体系的创新，目前磷酸铁锂电池、三元锂电池、锰酸锂电池和钴酸锂电池等锂电池为现阶段主流的技术路线，新型技术路径如氢燃料电池、固态锂离子电池、钠离子电池等正处于商业化初期阶段。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'产品名': {'方形电池': 1, '圆柱电池': 1, '软包电池': 1}}, {'技术名': {'电芯封装工艺': 1, '电池封装工艺': 1}}, {'行业名': {'工程领域': 1}}], 'text': '结构创新属于工程领域的创新，包括电芯封装工艺以及电池成组方式创新，其中电池封装工艺技术路径主要包括方形电池、软包电池、圆柱电池。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'行业名': {'动力电池': 1}}], 'text': '在动力电池领域，电池成组方式主要朝无模组化方向发展。'}]}, {'index': 31, 'sentences': [{'entity_subject': None, 'coref_subject': None, 'entities': [{'产品名': {'电连接产品': 1}}, {'行业名': {'电连接行业': 1}}], 'text': '上述技术路线变化趋势及对公司的具体影响如下：公司生产的电连接产品是构成电气系统的基础组件，是形成电路闭环并完成其他功能的重要组成部分，因此公司所处的电连接行业在产业链中拥有重要的地位和作用。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'产品名': {'铜铝': 1}}, {'行业名': {'电连接行业': 2, '新能源汽车': 1}}], 'text': '电连接行业上游原材料主要为铜铝等有色金属、电子材料、绝缘材料等，下游为新能源汽车、电化学储能、轨道交通、工业变频、新能源发电等行业，如下图所示：电连接行业上游原材料主要包括铜铝等有色金属、电子材料、绝缘材料等，原材料的价格变化将直接影响采购成本，从而影响行业整体的利润水平。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'产品名': {'铝': 1, '铜': 1}}], 'text': '我国铜、铝加工产能位居全球首位，市场供应充足，原材料价格受宏观经济、市场供求关系等因素影响存在一定波动。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'产品名': {'绝缘膜': 2, '电子材料': 1, '复合母排': 1}}], 'text': '除复合母排部分绝缘膜需要进口外，电池连接系统生产所需绝缘膜、电子材料等均来源于国内市场，市场供应充足。'}]}, {'index': 32, 'sentences': [{'entity_subject': None, 'coref_subject': None, 'entities': [{'行业名': {'新能源汽车': 1}}], 'text': '电连接行业下游分布广泛，主要涉及新能源汽车、电化学储能、轨道交通、工业变频、新能源发电等行业，上述行业与宏观经济政策、市场需求状况密切相关。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [], 'text': '下游行业发展前景详见本节“二、发行人所处行业的基本情况和竞争状况”之'}]}, {'index': 33, 'sentences': [{'entity_subject': None, 'coref_subject': None, 'entities': [], 'text': '“（三）所属细分行业的技术水平及特点、进入本行业主要壁垒、行业发展态势、面临机遇与风险、行业周期性特征，以及在产业链中的地位和作用，与上、下游行业之间的关联性”之'}]}, {'index': 34, 'sentences': [{'entity_subject': None, 'coref_subject': None, 'entities': [], 'text': '“4、下游主要行业市场前景”。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'产品名': {'锂电池': 1, '电池连接系统': 1}}, {'技术名': {'电池连接系统': 1}}, {'行业名': {'储能': 1, '新能源汽车': 1}}], 'text': '场地位、竞争优势与劣势，发行人与同行业可比公司的比较情况电池连接系统伴随锂电池在新能源汽车、储能等领域的规模化应用而发展，行业起步较晚，但发展速度较快，行业竞争主要围绕满足电池结构创新要求以及降低电池应用成本展开。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'行业名': {'新能源': 1}}], 'text': '尽管近年来新能源市场发展火热，吸引了众多厂商布局相关产业链上下游，但国内电池连接系统主要市场份额仍由少数技术创新能力较强、具备规模量产和产业化应用经验的厂商占据。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'产品名': {'复合母排': 1}}, {'行业名': {'复合母排产业': 1}}], 'text': '复合母排产业发展源于高频化、大功率功率器件的广泛应用和企业强大的技术研发实力与工艺积淀，下游客户主要为大型电气设备厂商，行业技术门槛较高，目前行业竞争格局较为稳定。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'公司名': {'壹连科技': 1}}, {'时间': {'2011年12月': 1}}], 'text': '公司各主要产品的主要竞争对手情况如下：壹连科技成立于 2011年12月，是一家集电连接组件研发、设计、生产、销售、服务于一体的产品及解决方案提供商。'}, {'entity_subject': None, 'coref_subject': '公司', 'entities': [{'产品名': {'消费电子': 1, '动力传输组件': 1, '工业设备': 1, '储能系统': 1, '电芯连接组件': 1, '低压信号传输组件': 1, '医疗设备': 1}}, {'行业名': {'新能源汽车': 1}}, {'地点': {'广东深圳': 1, '四川宜宾': 1, '江苏溧阳': 1, '福建宁德': 1, '浙江乐清': 1}}], 'text': '公司深耕电连接组件领域，目前已在广东深圳、福建宁德、江苏溧阳、四川宜宾及浙江乐清等多地建有生产基地，主要产品涵盖电芯连接组件、动力传输组件以及低压信号传输组件等各类电连接组件，形成了以新能源汽车为发展主轴，储能系统、工业设备、医疗设备、消费电子等多个应用领域齐头并进的产业发展格局。'}, {'entity_subject': '广州安博新能源科技有限公司', 'coref_subject': None, 'entities': [{'公司名': {'安捷利（番禺）电子实业有限公司': 1, '广州安博新能源科技有限公司': 1, '宁德博发电子科技有限公司': 1}}, {'产品名': {'FPC': 1}}, {'时间': {'2020年2月': 1}}], 'text': '广州安博新能源科技有限公司成立于2020年2月，由FPC供应商安捷利（番禺）电子实业有限公司与宁德博发电子科技有限公司合资建立。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'产品名': {'热压电芯管理模组': 1, '新能源电池组件': 1, '叠层母排': 1, '传统电芯管理模组': 1}}], 'text': '公司主要产品包含新能源电池组件、传统电芯管理模组、热压电芯管理模组、叠层母排等。'}]}, {'index': 35, 'sentences': [{'entity_subject': '美国安费诺集团', 'coref_subject': None, 'entities': [{'公司名': {'美国安费诺集团': 1}}, {'产品名': {'传感器': 1, '光纤连接器': 1, '互联系统': 1, '模块': 1, '电气': 1, '同轴': 1, '特种高速数据电缆': 1, '天线': 1, '电子': 1}}, {'时间': {'1932 年': 1}}, {'地点': {'美国康涅狄格州': 1}}], 'text': '美国安费诺集团创立于 1932 年，是全球最大的连接器制造商之一，总部位于美国康涅狄格州，主要业务为研发、生产及销售电气、电子、光纤连接器，互联系统、天线、传感器及基于传感器的模块，同轴及特种高速数据电缆等产品。'}]}, {'index': 36, 'sentences': [{'entity_subject': '安费诺（宁德）电子有限公司', 'coref_subject': None, 'entities': [{'公司名': {'安费诺集团': 1, '安费诺（宁德）电子有限公司': 1}}, {'产品名': {'模块': 1, '连接器': 1, '电池': 1, '传感器': 1, '组装件': 1, '传感器信号传输器件': 1, '线束': 1, '电源器件': 1}}, {'时间': {'2015年10月': 1}}], 'text': '安费诺（宁德）电子有限公司为安费诺集团旗下子公司之一，于 2015年10月成立，主要产品包含传感器及有关的组装电子器件与电池，电源配套的连接器，线束，电源器件及组装件，传感器信号传输器件及模块。'}]}, {'index': 37, 'sentences': [{'entity_subject': None, 'coref_subject': '公司', 'entities': [{'公司名': {'罗杰斯': 1}}, {'产品名': {'注塑': 1, '电池包连接': 1, '逆变器': 1, 'ROLINX®母线排': 1, '弹性材料解决方案': 1, '柔性母线排': 1, '功率变流器': 1, '叠层': 1, '电池模组': 1, '粉末涂层': 1}}, {'技术名': {'ROLINX®母线排技术': 1}}, {'行业名': {'先进材料': 1}}, {'时间': {'1832 年': 1}}, {'地点': {'美国亚利桑那州': 1}}], 'text': '罗杰斯公司成立于 1832 年，是先进材料领域的全球技术领导者，总部位于美国亚利桑那州，业务范围涵盖先进电子解决方案、弹性材料解决方案、先进互联解决方案，其中 ROLINX®母线排技术在全球处于行业领先地位，主要解决方案有叠层、粉末涂层、注塑、柔性母线排等，可应用于电池模组和电池包连接、功率变流器和逆变器等。'}]}, {'index': 38, 'sentences': [{'entity_subject': '罗杰斯科技（苏州）有限公司', 'coref_subject': None, 'entities': [{'公司名': {'罗杰斯': 1, '罗杰斯科技（苏州）有限公司': 1}}, {'产品名': {'配电定制分层母线排': 1, '汽车油箱': 1, '高频线路板材料': 1, '高性能泡沫材料': 1, '雷达装置系统': 1, '智能手机': 1, '合成橡胶部件': 1, '功率放大器': 1, '汽车': 1, '飞机': 1, '无线电基站': 1, '铁路运输内饰': 1, '浮标检测器': 1}}, {'技术名': {'能量管理': 1, '快速数字处理系统': 1}}, {'时间': {'2002 年': 1}}, {'地点': {'亚洲': 1}}], 'text': '罗杰斯科技（苏州）有限公司于 2002 年成立，是罗杰斯公司在亚洲的制造中心和总部，产品主要包括用于无线电基站、功率放大器、雷达装置系统和快速数字处理系统的高频线路板材料；用于铁路轨道交通、混合动力、风能太阳能转换等领域的配电定制分层母线排；用于智能手机密封和能量管理、飞机和铁路运输内饰、汽车及消费品等领域的高性能泡沫材料；以及用于汽车油箱等处的浮标检测器和用于打印领域的合成橡胶部件等。'}]}, {'index': 39, 'sentences': [{'entity_subject': '浙江赛英电力科技有限公司', 'coref_subject': None, 'entities': [{'公司名': {'浙江赛英电力科技有限公司': 1, '赛晶科技集团有限公司': 1}}, {'产品名': {'工业电气母排': 1, 'CCS 集成盖板': 1, '控制器层叠母排': 1}}, {'行业名': {'工业变频': 1, '电动汽车': 1, '光伏发电': 1, '风力发电': 1, '轨道交通': 1}}, {'时间': {'2011 年 5 月': 1}}, {'地点': {'浙江': 1}}], 'text': '浙江赛英电力科技有限公司成立于 2011 年 5 月，是赛晶科技集团有限公司生产的工业电气母排产品应用于轨道交通、电动汽车、工业变频、风力发电与光伏发电领域，同时生产 CCS 集成盖板、控制器层叠母排等产品。'}]}, {'index': 40, 'sentences': [{'entity_subject': '上海维衡精密电子股份有限公司', 'coref_subject': None, 'entities': [{'公司名': {'上海维衡精密电子股份有限公司': 1}}, {'产品名': {'母排': 1, '注塑零部件': 1, '连接器': 1, '弹片': 1, '屏蔽罩': 1, '支架': 1}}, {'行业名': {'工业': 2, '通讯电子': 2, '安防': 2, '汽车': 2}}, {'时间': {'2007年1月 10日': 1}}], 'text': '上海维衡精密电子股份有限公司成立于 2007年1月 10日，专注于精密模具及精密冲压、注塑电子零组件产品研发、设计、生产和销售，产品覆盖通讯电子、汽车、工业、安防四大行业，涉及母排、屏蔽罩、连接器、弹片、支架等 50 多个系列，面向全球为通讯电子、汽车、工业、安防等各行业客户提供高品质的精密五金冲压、注塑零部件及组件绿色解决方案。'}]}, {'index': 41, 'sentences': [{'entity_subject': None, 'coref_subject': None, 'entities': [{'公司名': {'壹连科技': 5}}, {'产品名': {'电芯连接组件': 2, '电池连接系统': 3, 'CCS': 1, '电动助力车': 1}}], 'text': '除壹连科技外，上述其他竞争对手未公开销售收入、产品产量、经营策略等信息，公司与壹连科技在营业收入、同类产品收入、同类产品产量、经营策略等方面对比如下：注：公司同类产品的选取口径为电池连接系统，壹连科技同类产品的选取口径为电芯连接组件，公司电池连接系统与壹连科技电芯连接组件产品类型及尺寸差异较大，销售单价高于壹连科技同类产品；公司电池连接系统产品产量含电动助力车CCS、不含配件入均快速增长。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [{'产品名': {'电池连接系统产品': 1, 'FPC 采样电池连接系统': 1, 'PCB采样电池连接系统': 1}}, {'技术名': {'热压合工艺': 2}}, {'时间': {'2020 年': 1, '2017 年': 1}}, {'地点': {'宁德': 1}}], 'text': '同类产品收入与产量对比方面，公司 2017 年推出PCB采样电池连接系统，首次将热压合工艺运用至电池连接系统领域，推广初期由于热压合工艺尚未得到大规模验证，销售规模相对较小；2020 年以来，随着公司 FPC 采样电池连接系统推出并在宁德时代成功应用，公司电池连接系统产品销售规模迅速提升，目前相关产品销售规模已与壹连科技相当。'}]}, {'index': 42, 'sentences': [{'entity_subject': None, 'coref_subject': '公司', 'entities': [{'产品名': {'电连接产品': 1}}, {'行业名': {'汽车行业': 1}}], 'text': '公司自成立以来一直专注于电连接产品的研发、生产与销售，始终坚持技术创新和产品升级，先后获得 IRIS 国际铁路行业质量管理体系认证、汽车行业质量管理体系认证，拥有“江苏省新型柔性叠层母排工程技术研究中心”，系具备多应用领域产品开发设计能力并能够实现高效柔性定制的高新技术企业。'}, {'entity_subject': None, 'coref_subject': None, 'entities': [], 'text': '依托技术研发、产品设计以及工艺制造能力，公司电连接产品在产品创新、多领域产品开发设计等方面具有较强的竞争优势，在业内具备较强的竞争力和行业地位。'}]}]

    # 构建链表
    ct = Cluster2Tree()
    # 打印根节点信息
    print(ct.build_cluster_tree(paragraphs))
