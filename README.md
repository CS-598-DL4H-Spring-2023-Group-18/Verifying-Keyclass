
# Verifying effectiveness of KeyClass for clinical notes categorization

### Sayar Ghosh Roy, Atharv Chandratre  

#### `{sayar3, atharvc2}@illinois.edu`

#### Group ID: 18
#### Paper ID: 103
  
# Introduction  
As part of the CS598 Deep Learning for Healthcare (Spring 2023) Final Project, our aim was to reproduce the paper, titled 'Classifying Unstructured Clinical Notes via Automatic Weak Supervision'. The goal of the paper is to alleviate the practice of manual diagnostic coding of clinical notes, a process that is time-consuming, expensive, and error-prone. To address this problem, the paper introduces KeyClass, a weakly-supervised text classification framework. KeyClass learns a text classification model from class label descriptions alone, eliminating the requirement for manually tagged documents. To assign code labels to specific texts, KeyClass leverages pre-trained language models and data programming frameworks. During the classification process, KeyClass creates certain interpretable heuristics based on keywords extracted from the available text data. Through the adoption of domain-specific language models, the KeyClass framework could also be tailored to classification tasks in other highly specialized domains. The comparison between KeyClass and other seminal weakly supervised text classification architectures demonstrates KeyClass's efficiency and adaptability.  
  
# Claims That We Evaulated

 - The KeyClass model effectively mines category-indicative terms from each ICD-9 category
 -  The KeyClass model is capable of achieving an average F1-score greater than the previous state-of-the-art, namely FasTag, for the weakly supervised multi-label classification task on MIMIC-III clinical notes data
 - *(Additional Ablation)* The proposed self-training (refining the downstream classifier using the complete training dataset) helps the overall classification performance on the MIMIC-III clinical notes dataset

# Running the code

## Dependencies

 - `snorkel`
 - `sentence-transformers`
 - `transformers`
 - `pyhealth`

The bash script described below will install these dependencies automatically.

## Data Download Instructions
We have hosted all of the data needed to run the experiments as a `.zip` file on Google Drive. Therefore, there are no explicit data download instructions. The bash script will pick up the necessary data and unzip it at the appropriate location.

## Pre-processing Code
The data stored as a `.zip` file hosted on Google Drive is already pre-processed. Therefore, no pre-processing code needs to be run. We have described the pre-processing method in the 'Data Description' section of the project report.

## Training and Evaluation Code
In order to run the code, the following process is to be followed:

### Running the code
 1. Download the respective 'final-run.sh' file to run the experiment you wish to run. If you wish to run the Multi-Hot setting, download the final-run.sh file located at `Multi-Hot/scripts/final-run.sh`.  If you wish to run the One-Versus-Not setting, download the final-run.sh file located at `One-Versus-Not/scripts/final-run.sh`. You do NOT need to clone the GitHub repo. The script will do this for you.
 2. Run `bash final-run.sh`. Note: if you are running it on Colab, make sure you are connected to a GPU runtime.
 3. The bash script will run all of the components of the experiment, including downloading the dataset, encoding it, labeling the data, training the model and saving the model results.

### Results Location
The results of the experiment will be stored in the `/Verifying-Keyclass/Keyclass/results/mimic/` directory. The results will be stored as `.txt` files. The results will be of the format `class number-(train or test)-(label or end model)-with-ground-truth-(self-trained or not not)-timestamp.txt`.

### Modifying the config files
The following config files are to be modified if the experimenter wishes to change the hyperparameters. The procedure is as follows:

1. Fork this repo.
2. Modify the following config files based on the experiment being performed:
	 - Multi-Hot: `Multi-Hot/config_files/config_mimic.yaml`
	 - One-Versus-Not: `One-Versus-Not/scripts/base_config_mimic.yaml`
3. Do read through the 'Computational Requirements' section of the report. In our experience, running the Multi-Hot experiment on Colab gives a *CUDA out of memory* error. But One-Versus-Not works on Colab with reduced parameters. If you are running it on Google Colab, we recommend decreasing the end model batch size, end model epochs, and size of the dataset (but keeping the dataset size to atleast 1000).
4. Change the link to the appropriate repo in the `final-run.sh` script (line 4). You do not need to make any other modifications to this file.
5. Follow the instructions in the above 'Running the code' subsection.

## Pre-trained Model
Not applicable in our case

# Table of Results

![Ablation Study: Metrics achieved by the  KeyClass  model ](https://drive.google.com/uc?id=1Gyu5HckOzffkx3Q8s_i49kmNO7dn97br)
*Ablation Study: Metrics achieved by the KeyClass  model before self-training*

![Metrics achieved by the  KeyClass  model after fine-tuning the downstream classifier](https://drive.google.com/uc?id=15agPpgpyvJu_h5BxMsIMNbuuOpQFPYxn)
*Metrics achieved by the  KeyClass  model after fine-tuning the downstream classifier*

More Details about the results are given in the 'Results and Analysis' section of the project report.

# Original Paper
  
## Citation
```
@article{gao2022classifying,
  title={Classifying Unstructured Clinical Notes via Automatic Weak Supervision},
  author={Gao, Chufan and Goswami, Mononito and Chen, Jieshi and Dubrawski, Artur},
  journal={Machine Learning for Healthcare Conference},
  year={2022},
  organization={PMLR}
}
```
#### [Link to original paper](https://proceedings.mlr.press/v182/gao22a/gao22a.pdf)

#### [Link to original paper's codebase](https://github.com/autonlab/KeyClass)

#### [Link to the colab notebook](https://colab.research.google.com/drive/1mjFFoE7jwR9bNADCzM8pwRl4JPrI9NGX)

#### [Link to the YouTube Video](https://www.youtube.com/watch?v=KBATJu55oqc&ab_channel=AtharvChandratre)
  
---
