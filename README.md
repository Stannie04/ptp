# PTP: Partiture to Performance using Speech Synthesis with Encoder-Decoder models

This repository provides all code used for training a model through the PTP process. The model uses the Tacotron 2 acoustic model and WaveGlow as a vocoder to convert sheet music to an expressive violin performance. The dataset provided is a modified version of the Bach Violin dataset, slightly altered to simplify preprocessing.

## Setup
```mkdir data filelists```

```pip install -r requirements.txt```


## Preprocessing

The following command will convert the MXL files in the dataset to PTXT, split them by the given argument and create corresponding audio clips. These are then put into train and test filelists for training.

```python prepare_data.py <measures per split>```

## Inference

Inference on the model can be done through the use of the tools provided by Tacotron 2 and WaveGlow. See their corresponding repositories for more information.


To run an accuracy metric on generated mel-spectrograms given a prompted input or plot mel-spectrograms and alignment charts, run the following:

```python src/inference.py /path/to/model```