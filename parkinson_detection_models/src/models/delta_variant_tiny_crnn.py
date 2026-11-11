import torch
from torch import nn

from src.models.tiny_crnn import TinyCRNN


class DeltaLFBE(nn.Module):
    """
    Non-trainable conv layer with a 2x1x1 kernel and [-1, 1] weights
    that subtracts adjacent input frames.
    Input  : (B, 1, T+1, F)
    Output : (B, 1, T,   F)
    """
    def __init__(self):
        super().__init__()
        self.conv = nn.Conv2d(1, 1, kernel_size=(2, 1), bias=False)
        with torch.no_grad():
            # weights = [-1, 1] over the time dimension
            self.conv.weight.copy_(torch.tensor([[[[-1.0], [1.0]]]]))
        for p in self.conv.parameters():
            p.requires_grad = False

    def forward(self, x):
        return self.conv(x)

### Variant of Tiny CRNNwith the Delta-LFBE preprocessing layer in front of the original CRNN ###

class DeltaLFBETinyCRNN(nn.Module):
    """CRNN-239k with the Delta-LFBE preprocessing layer in front."""
    def __init__(self, n_mels=64, n_frames=101, **kwargs):
        super().__init__()
        self.delta = DeltaLFBE()
        # After delta we have 100 frames going into the original CRNN
        self.crnn = TinyCRNN(n_mels=n_mels, n_frames=n_frames - 1, **kwargs)

    def forward(self, x):
        # x: (B, 1, 101, F)
        x = self.delta(x)                       # (B, 1, 100, F)
        return self.crnn(x)
