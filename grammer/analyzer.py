import hanlp
import jieba

# hanlp.pretrained.srl.ALL
dep = hanlp.load(hanlp.pretrained.dep.CTB9_DEP_ELECTRA_SMALL)


def find_suj(text):
    lines = text.split('\n')

    for line in lines:
        if 'nsubj' in line:
            items = line.split('|')
            item = items[2].strip()
            return item
    return None

texts = [
"专业中间件行业呈现较好的竞争格局，主流厂商包括东方通、中创、宝兰德、普元、金蝶等已树立起一定的竞争壁垒",
"""公司曾多次牵头承担“核高基”科技重大专项、且曾负责工信部项目D，所形成的产品通过信创工程已率先在党政、军工等领域实现国产中间件替换，
产品服务于中共中央办公厅、国家发改委、水利部、银保监会等重点单位及中国银行、潍柴动力、南方电网等重点行业龙头客户，在党政、军工领域具备较强的竞争优势。"""
]

for text in texts:
    #jieba.add_word('安集微电子科技')
    words = jieba.lcut(text)

    tree = dep(words)
    print('Subject is: ', find_suj(tree.to_markdown()))
