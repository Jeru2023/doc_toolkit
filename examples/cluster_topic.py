# -*- encoding: utf-8 -*-
from doc_splitter import DocSplitter
from tools import utils

#doc_name = '南非移民医疗保健.txt'
#doc_name = '埃斯顿集团.txt'
doc_name = '新闻原始数据底层.txt'
doc = utils.load_text(doc_name)

doc = doc.replace('\n', '')
print(doc)
doc_splitter = DocSplitter()
nodes = doc_splitter.split(doc, 1000, with_entities=False)

i = 1
for node in nodes:
    print('*** chunk {i} ***'.format(i=i))
    print(node['tags'])
    # print(node['index'])
    print(doc_splitter.merge_paragraph_text(node['paragraphs']))
    print('--------------------------------\n')
    i += 1
