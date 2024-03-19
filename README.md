<!-- ABOUT THE PROJECT -->
## About The Project

### Sentence Segement
### Paragraph Segement
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
6. Fix bert nlp seg model bug for chinese text<br>
   If you encounter issues with the handling of English periods (full stops) during sentence segmentation in Chinese text, and you need to manually fix it, you can modify the sentence segmentation function in the local installation package. <br>
   
   Specifically, you can make changes to the cut_sentence function in <b>modelscope.pipelines.nlp.document_segmentation_pipeline</b>.<br>
   To address the problem, <b>replace the first line regular expression in the function</b>.
   ```sh
   def cut_sentence(self, para):
      # para = re.sub(r'([。！.!？\?])([^”’])', r'\1\n\2', para)  # noqa *
      para = re.sub(r'([。！!？\?])([^”’])|(\.)([^”’\d])', r'\1\n\2', para)  # noqa *
   ```

## Usage
### Sentence Split

### Paragraph Split

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
