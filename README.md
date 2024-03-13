<!-- ABOUT THE PROJECT -->
## About The Project

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
4. Download the Spacy Engnlish model.
   ```sh
   python -m spacy download en_core_web_sm
   ```
5. Install pytorch
   For non-GPU device
   ```sh
   pip install torch
   ```sh

   For GPU device
   Run 'nvidia-smi' to find out your CUDA version, for example my version is 12.1
   Then I should run below command to install pytorch with CUDA:
   ```sh
   pip install torch --pre -f https://download.pytorch.org/whl/nightly/cu121/torch_nightly.html
   ```sh
