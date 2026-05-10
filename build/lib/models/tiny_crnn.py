import torch
import torch.nn as nn
import torch.nn.functional as F
import math


class ScaledDotProductAttention(nn.Module):
    """
    Scaled dot-product attention as described in Section 2.2.

    Attention(Q, K, V) = softmax(QK^T / sqrt(d_K)) V

    Three linear layers project the recurrent layer output into
    K, Q, V with dimensions d_K = d_Q = d_V = d.
    """
    def __init__(self, hidden_dim):
        super().__init__()
        self.d_k = hidden_dim
        self.W_q = nn.Linear(hidden_dim, hidden_dim, bias=False)
        self.W_k = nn.Linear(hidden_dim, hidden_dim, bias=False)
        self.W_v = nn.Linear(hidden_dim, hidden_dim, bias=False)

    def forward(self, x):
        # x: (B, T', d)
        Q = self.W_q(x)
        K = self.W_k(x)
        V = self.W_v(x)

        # (B, T', T')
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)
        attn = F.softmax(scores, dim=-1)

        # (B, T', d)
        out = torch.matmul(attn, V)
        return out


class ConvBlock(nn.Module):
    """Convolutional block: Conv2d -> BatchNorm -> ReLU -> Dropout"""
    def __init__(self, in_ch, out_ch, kernel_size, stride=(1, 1),
                 padding=0, dropout=0.3):
        super().__init__()
        self.conv = nn.Conv2d(in_ch, out_ch, kernel_size=kernel_size,
                              stride=stride, padding=padding)
        self.bn = nn.BatchNorm2d(out_ch)
        self.relu = nn.ReLU(inplace=True)
        self.drop = nn.Dropout(dropout)

    def forward(self, x):
        return self.drop(self.relu(self.bn(self.conv(x))))


class TinyCRNN(nn.Module):
    """
    Tiny-CRNN architecture for wakeword detection.

    Pipeline:
        Input I  : (B, 1, T=100, F=64)            # LFBE features
        Conv FE  : -> D  in (B, c', T', f')
        Reshape  : -> D' in (B, T', f'*c')
        GRU      : -> L  in (B, T', d)
        Attention: -> U  in (B, T', d)
        Sum over T' axis -> (B, d)
        FC layers -> logits (B, num_classes)

    The default config below corresponds to CRNN-239k from the paper:
      - 3 conv layers
      - conv output 10 x 512  (T'=10, f'*c'=512 after reshape)
      - GRU hidden d=64
      - Receptive field ~28 input frames going into the recurrent layer
    """
    def __init__(self,
                 n_mels=64,
                 n_frames=100,
                 conv_channels=(64, 64, 64),
                 conv_kernels=((5, 5), (5, 5), (10, 4)),
                 conv_strides=((1, 2), (2, 2), (1, 1)),
                 gru_hidden=64,
                 fc_hidden=64,
                 num_classes=2,
                 dropout=0.3,
                 use_attention=True):
        super().__init__()
        self.use_attention = use_attention
        self.gru_hidden = gru_hidden

        # ---- Convolutional front-end ----
        layers = []
        in_ch = 1
        for out_ch, k, s in zip(conv_channels, conv_kernels, conv_strides):
            layers.append(ConvBlock(in_ch, out_ch, kernel_size=k,
                                    stride=s, padding=0, dropout=dropout))
            in_ch = out_ch
        self.conv = nn.Sequential(*layers)

        # Determine conv output shape with a dummy forward pass
        with torch.no_grad():
            dummy = torch.zeros(1, 1, n_frames, n_mels)
            cout = self.conv(dummy)            # (1, c', T', f')
            _, c_out, t_out, f_out = cout.shape
        self.t_out = t_out
        self.feat_dim = c_out * f_out          # f' * c'

        # ---- Recurrent layer (GRU) ----: layer que tiene memoria de ventana de step (t-1) pasados: a-> lex -> a
        # Input to GRU: (B, T', f'*c')
        self.gru = nn.GRU(input_size=self.feat_dim,
                          hidden_size=gru_hidden,
                          num_layers=1,
                          batch_first=True)

        # ---- Scaled dot-product attention ----
        if use_attention:
            self.attention = ScaledDotProductAttention(gru_hidden)

        # ---- Fully-connected head ----
        self.fc = nn.Sequential(
            nn.Linear(gru_hidden, fc_hidden),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(fc_hidden, num_classes),
        )

    def forward(self, x):
        # x: (B, 1, T, F)
        D = self.conv(x)                       # (B, c', T', f')
        B, c, t, f = D.shape

        # Permute to (B, T', c', f') then flatten last two dims to (B, T', c'*f')
        D_prime = D.permute(0, 2, 1, 3).contiguous().view(B, t, c * f)

        # GRU
        L, _ = self.gru(D_prime)               # (B, T', d)

        # Attention
        if self.use_attention:
            U = self.attention(L)              # (B, T', d)
        else:
            U = L

        # Sum across time
        pooled = U.sum(dim=1)                  # (B, d)

        logits = self.fc(pooled)               # (B, num_classes)
        return logits


def count_parameters(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


