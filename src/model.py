import torch
from scipy.io.wavfile import write
from torchaudio.models import Tacotron2

def main():
    tacotron2 = Tacotron2()
    waveglow = torch.hub.load('nvidia/DeepLearningExamples:torchhub', 'nvidia_waveglow', trust_repo=True)

    tacotron2.to('cuda')
    waveglow.to('cuda')

if __name__=='__main__':
    main()