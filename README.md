<!-- ABOUT THE PROJECT -->
## About The Project

### Sentence Segement
### Paragraph Segement
```sh  
def cut(text, split_mode='bert', with_tags=False, with_entities=False, chunk_size=800,
      top_k=5, extract_mode='text_rank'):
  """
  :param text: text to be cut
  :param split_mode: 'bert', 'natural' or 'brutal'
  :param with_tags: if keyword tags required.
  :param with_entities: if entity extraction required
  :param chunk_size: applicable only for 'brutal'
  :param top_k: number of tags to extract
  :param extract_mode: 'text_rank' or 'tfidf'
  :return: a list of dictionaries, each dictionary represents a paragraph
  """
```sh  
#### Segment Methods
1. Natural Cut<br>
   Content splitted by '\n'
   
3. Brutal Cut<br>
   Content splitted by specified chunk size
   
5. Senantic Cut<br>
   Content splitted by bert senmantic model, best effect but also time consuming.

#### Segement Router
Before segmentation, first calculate:<br>
<li>the length of the article</li>
<li>the average sentence length</li>
<li>the average paragraph length</li>
<li>the variance of sentence lengths and paragraph lengths. </li>
<br>
These statistics can be used to automatically determine the appropriate segmentation method.

### Topic Clustering
#### K-Means and Principle Component Analysis
#### DBScan and Multidimensional Scaling
#### Hierarchical Clustering with WARD

### Coreference Resolution
Get "trained_coref_model" from Jeru and place it in "models" folder.

<!-- GETTING STARTED -->
## Getting Started

### Installation

1. Create independent Python Environment.
   ```sh    
    conda create -n doc python=3.9.17
    conda activate doc
   ```
2. Clone the repo
   ```sh
   git clone git@github.com:Jeru2023/doc_toolkit.git
   ```
3. Install packages
   ```sh
   pip install -r requirements.txt
   ```
4. Download the Spacy English model.
   ```sh
   python -m spacy download en_core_web_sm
   ```
5. Install pytorch manually<br>
   For non-GPU device:
   ```sh
   pip install torch
   ```

   For GPU device:<br>
   Run 'nvidia-smi' to find out your CUDA version, for example my version is 12.1<br>
   In this case I should run below command to install pytorch with CUDA.
   ```sh
   pip install torch --pre -f https://download.pytorch.org/whl/nightly/cu121/torch_nightly.html
   ```
6. Ask 宏宇老师 or Jeru for the NER finetune model, rename it to "uie_model_best" then put it in "models" folder

## Usage
### Sentence Split

### Paragraph Split

```python
from paragraph_splitter.paragraph_cutter import ParagraphCutter

pc = ParagraphCutter()

content = "some text input..."
results = pc.cut(content, with_tags=True, with_entities=True)

for result in results:
   print(result["paragraph"])
   print(result["tags"])
   print(result["entities"])
   print('----------------')
```
### Entity Extraction

### Clustering

### Coreference Resolution
```python
from coref.coref_model import CorefModel

coref_model = CorefModel()
content = "some text input..."
coref_dict = coref_model.predict(content)

print(content)
# check verbose detail printed out in friendly version
print(coref_model.show_verbose(coref_dict))
```
