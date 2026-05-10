import torch
from torch import nn
from torch.compiler import F

from src.models.tiny_crnn import TinyCRNN

#option 1: parallel decoders
#option 2: high-dim streaming GRU with vectorized overlapping windows
class ParallelStreamingCRNN(nn.Module):
    """
    Streaming inference with t' parallel GRU decoders.

    The convolutional front-end is shared (and ideally implemented with
    a ring buffer for efficiency, see [Rybakov et al., 2020]).
    The GRU layer is replicated t' times so that decoder i consumes
    the time-window starting at frame i.

    Only after t' new time steps arrive do we reset all GRU states.
    """
    def __init__(self, base_model: TinyCRNN):
        super().__init__()
        self.conv = base_model.conv
        self.t_prime = base_model.t_out
        self.feat_dim = base_model.feat_dim
        self.gru_hidden = base_model.gru_hidden
        self.use_attention = base_model.use_attention

        # t' identical GRU decoders (same trained weights)
        self.gru_decoders = nn.ModuleList()
        for _ in range(self.t_prime):
            g = nn.GRU(self.feat_dim, self.gru_hidden, batch_first=True)
            g.load_state_dict(base_model.gru.state_dict())
            self.gru_decoders.append(g)

        if self.use_attention:
            self.attention = base_model.attention
        self.fc = base_model.fc

        # Per-decoder hidden state and per-decoder buffer (list of time steps)
        self.reset_state()

    def reset_state(self):
        self.hidden = [None] * self.t_prime
        self.buffers = [[] for _ in range(self.t_prime)]
        self.global_step = 0

    @torch.no_grad()
    def step(self, time_step):
        """
        Push one new time step (B, feat_dim) coming out of the conv front-end
        into the parallel decoders. Returns the latest posterior or None if
        no decoder produced a full output yet.
        """
        out_posterior = None
        for i in range(self.t_prime):
            if self.global_step >= i:                        # decoder i is active
                self.buffers[i].append(time_step)
                if len(self.buffers[i]) == self.t_prime:
                    seq = torch.stack(self.buffers[i], dim=1)  # (B, t', feat)
                    L, _ = self.gru_decoders[i](seq)           # (B, t', d)
                    if self.use_attention:
                        U = self.attention(L)
                    else:
                        U = L
                    pooled = U.sum(dim=1)                       # (B, d)
                    out_posterior = F.softmax(self.fc(pooled), -1)
                    self.buffers[i] = []                       # ready to refill

        self.global_step += 1
        # Reset all states/buffers every t' * t' steps (paper convention)
        if self.global_step % (self.t_prime * self.t_prime) == 0:
            self.reset_state()
        return out_posterior
    
class HighDimStreamingGRU(nn.Module):
    """
    Vectorized GRU that processes t' overlapping windows at once.
    During inference we wait for (2*t' - 1) time steps from the conv FE,
    arrange them into a tensor of shape (t', t', feat_dim) of overlapping
    windows, and run a single batched GRU over that tensor.

    This avoids replicating the GRU weights as in the parallel-decoder
    approach.
    """
    def __init__(self, base_gru: nn.GRU, t_prime: int):
        super().__init__()
        self.gru = base_gru                  # reuse trained GRU
        self.t_prime = t_prime

    @torch.no_grad()
    def forward(self, conv_out_2tm1):
        """
        conv_out_2tm1: (B, 2*t'-1, feat_dim)
        Returns: (B, t', t', d) hidden states for every overlapping window.
        """
        B, T, F_ = conv_out_2tm1.shape
        assert T == 2 * self.t_prime - 1

        # Build overlapping windows: window i = frames [i : i + t']
        windows = torch.stack(
            [conv_out_2tm1[:, i:i + self.t_prime, :] for i in range(self.t_prime)],
            dim=1,
        )  # (B, t', t', feat_dim)

        # Flatten the (B, t') batch dimension so the GRU treats every
        # window as an independent sequence (vectorization)
        flat = windows.view(B * self.t_prime, self.t_prime, F_)
        out, _ = self.gru(flat)                            # (B*t', t', d)
        out = out.view(B, self.t_prime, self.t_prime, -1)  # (B, t', t', d)
        return out