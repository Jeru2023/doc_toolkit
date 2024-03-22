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

text = """
安集微电子科技经过多年研发，已建立起多样化的配方工艺和产品结构，能够满足不同太阳能电池片客户对于添加剂的多样化需求。
"""
jieba.add_word('安集微电子科技')
words = jieba.lcut(text)

tree = dep(words)

print('Subject is: ', find_suj(tree.to_markdown()))
