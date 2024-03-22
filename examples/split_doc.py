import doc_splitter
from tools import utils

doc_name = '西典新能招股书.txt'
doc = utils.load_text(doc_name)

doc_splitter = doc_splitter.DocSplitter()
nodes = doc_splitter.split(doc, 1000)
chunks_with_entities = doc_splitter.append_entities_to_paragraph(nodes)
chunks = doc_splitter.append_tags_to_cluster(chunks_with_entities)

i = 0
for chunk in chunks:
    print('*** chunk {i} ***'.format(i=i))
    print(chunk)
    print('--------------------------------\n')
    i += 1

