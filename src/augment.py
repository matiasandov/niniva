import torch
import torch.nn as nn


class SpecAugment(nn.Module):
    """
    SpecAugment: time and frequency masking for log-mel spectrograms.
    Operates on tensors of shape (B, 1, n_frames, n_mels) — i.e. the
    output of LFBEFeatureExtractor and the input of TinyCRNN.

    Reference: Park et al., 2019 (https://arxiv.org/abs/1904.08779)
    """

    def __init__(self,
                 freq_mask_param=8,
                 n_freq_masks=2,
                 time_mask_param=25,
                 n_time_masks=2,
                 time_mask_ratio=0.2,
                 mask_value=0.0,
                 prob=1.0):
        """
        Args:
            freq_mask_param  (F) : max width of a frequency mask (in bins)
            n_freq_masks         : number of frequency masks per sample
            time_mask_param  (T) : max width of a time mask (in frames)
            n_time_masks         : number of time masks per sample
            time_mask_ratio  (p) : upper bound on fraction of frames masked
            mask_value           : value to fill masked regions with
                                   (use 0.0 if features are mean-normalized)
            prob                 : probability of applying SpecAugment to a
                                   given sample (1.0 = always)
        """
        super().__init__()
        self.F = freq_mask_param
        self.mF = n_freq_masks
        self.T = time_mask_param
        self.mT = n_time_masks
        self.p = time_mask_ratio
        self.mask_value = mask_value
        self.prob = prob

    @torch.no_grad()
    def forward(self, x):
        # Only augment in training mode
        if not self.training:
            return x

        # x: (B, 1, n_frames, n_mels)
        B, _, n_frames, n_mels = x.shape
        max_time_mask_total = int(self.p * n_frames)

        for b in range(B):
            if torch.rand(1).item() > self.prob:
                continue

            # ----- Frequency masking -----
            for _ in range(self.mF):
                f = torch.randint(0, self.F + 1, (1,)).item()
                if f == 0 or f >= n_mels:
                    continue
                f0 = torch.randint(0, n_mels - f, (1,)).item()
                x[b, :, :, f0:f0 + f] = self.mask_value

            # ----- Time masking (with total-budget cap) -----
            time_masked = 0
            for _ in range(self.mT):
                remaining = max_time_mask_total - time_masked
                if remaining <= 0:
                    break
                t_max = min(self.T, remaining)
                t = torch.randint(0, t_max + 1, (1,)).item()
                if t == 0 or t >= n_frames:
                    continue
                t0 = torch.randint(0, n_frames - t, (1,)).item()
                x[b, :, t0:t0 + t, :] = self.mask_value
                time_masked += t

        return x
