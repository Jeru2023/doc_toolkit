# -*- encoding: utf-8 -*-
from doc_splitter import DocSplitter
from tools import utils

doc_name = '西典新能招股书.txt'
doc = utils.load_text(doc_name)

doc_splitter = DocSplitter()
nodes = doc_splitter.split(doc, 1000)

i = 1
for node in nodes:
    print('*** chunk {i} ***'.format(i=i))
    print(node)
    print('--------------------------------\n')
    i += 1
