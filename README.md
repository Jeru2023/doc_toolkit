<!-- ABOUT THE PROJECT -->
## About The Project

### Paragraph Segementation
#### Segment Methods


#### Segement Router
Before segmentation, first calculate:<br>
<li>the length of the article</li>
<li>the average sentence length</li>
<li>the average paragraph length</li>
<li>the variance of sentence lengths and paragraph lengths. </li>
<br>
These statistics can be used to automatically determine the appropriate segmentation method.

<!-- GETTING STARTED -->
## Getting Started

### Installation

1. Create independent Python Environment.
   ```sh    
    conda create -n doc python=3.9
    conda activate doc
   ```
2. Clone the repo
   ```sh
   git clone git@github.com:Jeru2023/doc_toolkit.git
   ```
3. Install packages
   ```sh
   install -r requirements.txt
   ```
4. Download the Spacy English model.
   ```sh
   python -m spacy download en_core_web_sm
   ```
5. Install pytorch<br>
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
   To address the problem, <b>remove the decimal point from the first regular expression in the function</b>. 
