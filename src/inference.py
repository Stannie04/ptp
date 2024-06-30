import matplotlib.pylab as plt

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'tacotron2'))
import numpy as np
import torch

import librosa
import librosa.display

from  torch import nn

from data_utils import TextMelLoader
from hparams import create_hparams
from model import Tacotron2
from layers import TacotronSTFT, STFT
from audio_processing import griffin_lim
from train import load_model
from text import text_to_sequence
from waveglow.denoiser import Denoiser

def plot_mel(mel_data, filename, figsize=(16, 4)):
    """Plot the mel spectrogram."""

    fig, ax = plt.subplots(figsize=figsize)
    cax = ax.matshow(mel_data, interpolation='nearest', aspect='auto', cmap='inferno')
    fig.colorbar(cax)
    ax.invert_yaxis()
    plt.title('Mel spectrogram')
    plt.tight_layout()
    plt.savefig(f'misc_data/figures/{filename}.png')
    plt.close()


def plot_original_mel(score, hparams):
    """Plot the original mel spectrogram."""

    trainset = TextMelLoader(hparams.training_files, hparams)
    mel_spectrogram = trainset.get_mel(score)
    plot_mel(mel_spectrogram, "target_mel")

    return mel_spectrogram

def plot_alignments(alignments, filename):
    """Plot the attention alignments."""

    fig, ax = plt.subplots()
    cax = ax.matshow(alignments, interpolation='nearest', aspect='auto')
    fig.colorbar(cax)
    ax.invert_yaxis()
    plt.xlabel('Decoder timestep')
    plt.ylabel('Encoder timestep')
    plt.title('Attention alignment')
    plt.tight_layout()
    plt.savefig(f'misc_data/figures/{filename}.png')
    plt.close()


def load_synthesis_model(hparams):
    """Load the Tacotron2 model."""

    print("Loading Tacotron2 model...")
    checkpoint_path = sys.argv[1]
    model = load_model(hparams)
    model.load_state_dict(torch.load(checkpoint_path)['state_dict'])
    model.cuda().eval()
    print("Loaded Tacotron2 model")

    return model

def inference(model, text):
    """Inference on the Tacotron2 model."""

    sequence = np.array(text_to_sequence(text, ['ptp_cleaners']))[None, :]
    sequence = torch.autograd.Variable(torch.from_numpy(sequence)).cuda().long()

    _, mel_outputs_postnet, _, alignments = model.inference(sequence)

    return mel_outputs_postnet, alignments

def pad_mels(output_mel, target_mel):
    """Pad the tensors to have the same length. This is necessary to calculate the loss."""

    if output_mel.size(1) > target_mel.size(1):
        target_mel = torch.nn.functional.pad(target_mel, (0, output_mel.size(1) - target_mel.size(1)))
    elif output_mel.size(1) < target_mel.size(1):
        output_mel = torch.nn.functional.pad(output_mel, (0, target_mel.size(1) - output_mel.size(1)))

    output_mel = output_mel.to('cuda')
    target_mel = target_mel.to('cuda')

    return output_mel, target_mel

def get_accuracy(output_mel, target_mel):
    """Calculate the mean squared error between the output and target mel spectrograms."""

    output_mel.to('cuda')
    target_mel.to('cuda')
    return nn.MSELoss()(output_mel, target_mel)

def confidence_interval(losses):
    """Print confidence interval in the form " x +- y"""
    mean = np.mean(losses)
    std = np.std(losses)
    n = len(losses)
    return f"{mean:.2f} +- {1.96 * std / np.sqrt(n):.2f}"


def main():
    hparams = create_hparams()
    hparams.sampling_rate = 22050
    model = load_synthesis_model(hparams)

    with open("prompt.txt", "r") as file:
        line = file.readline()
    score, text = line.split('|')
    text = text.replace('\n', '')

    target_list = []
    digital_list = []
    for i in range(10000):

        mel_outputs_postnet, alignments = inference(model, text)


        target_mel = plot_original_mel(score, hparams)
        digital_mel = plot_original_mel("data/synth.wav", hparams)
        padded_target, padded_digital = pad_mels(digital_mel, target_mel)

        a = get_accuracy(padded_digital, padded_target)
        digital_list.append(a.float().data.cpu())
        print(f"Accuracy: {a}")
        print(f"Confidence interval: {confidence_interval(digital_list)}")

        with torch.no_grad():
            padded_output, padded_target = pad_mels(mel_outputs_postnet[0], target_mel)
            loss_target = get_accuracy(padded_output, padded_target)
            target_list.append(loss_target.float().data.cpu())
            print(f"\nTarget loss: {loss_target}")
            print(f"Target confidence interval: {confidence_interval(target_list)}")

            padded_output, padded_target = pad_mels(mel_outputs_postnet[0], digital_mel)
            loss_digital = get_accuracy(padded_output, padded_target)
            digital_list.append(loss_digital.float().data.cpu())
            print(f"Digital loss: {loss_digital}")
            print(f"Digital confidence interval: {confidence_interval(digital_list)}")


            plot_mel(mel_outputs_postnet.float().data.cpu().numpy()[0], "generated_mel")
            plot_alignments(alignments.float().data.cpu().numpy()[0].T, "alignments")

if __name__ == "__main__":
    main()