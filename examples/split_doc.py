import doc_splitter
from tools import utils

doc_name = '西典新能招股书.txt'
#doc_name = '中创股份研报.txt'
doc = utils.load_text(doc_name)

doc_splitter = doc_splitter.DocSplitter()
chunks = doc_splitter.split(doc, 2000)


i = 0
for chunk in chunks:
    print('*** chunk {i} ***'.format(i=i))
    print(chunk)
    print('--------------------------------\n')
    i += 1

