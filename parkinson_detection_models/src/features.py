import torch
import torch.nn as nn
import torchaudio
import torchaudio.transforms as T


class LFBEFeatureExtractor(nn.Module):
    """
    Log Mel-Filter Bank Energies (LFBE) feature extractor.

    Matches the paper's setup:
      - 25 ms window, 10 ms hop
      - 64 mel bins (250k budget) or 20 mel bins (50k budget)
      - 100 frames ≈ 1 second of audio

    Input  : waveform (B, num_samples)   raw audio at `sample_rate`
    Output : features (B, 1, n_frames, n_mels)   ready for Tiny-CRNN
    """
    def __init__(self,
                 sample_rate=16000,
                 n_mels=64,
                 win_length_ms=25,
                 hop_length_ms=10,
                 n_frames=100,
                 f_min=20.0,
                 f_max=8000.0,
                 normalize=True):
        super().__init__()
        self.sample_rate = sample_rate
        self.n_frames = n_frames
        self.normalize = normalize

        win_length = int(sample_rate * win_length_ms / 1000)   # 400 @ 16 kHz
        hop_length = int(sample_rate * hop_length_ms / 1000)   # 160 @ 16 kHz
        n_fft = 1
        while n_fft < win_length:
            n_fft *= 2                                         # 512 @ 16 kHz

        self.mel = T.MelSpectrogram(
            sample_rate=sample_rate,
            n_fft=n_fft,
            win_length=win_length,
            hop_length=hop_length,
            n_mels=n_mels,
            f_min=f_min,
            f_max=f_max,
            power=2.0,                # power spectrogram
            center=True,
        )
        # log(x + eps) is more stable than AmplitudeToDB for low-energy bins
        self.eps = 1e-6

    def forward(self, waveform):
        # waveform: (B, num_samples)  — mono
        if waveform.dim() == 3:                # (B, 1, N) -> (B, N)
            waveform = waveform.squeeze(1)

        mel_spec = self.mel(waveform)          # (B, n_mels, T)
        log_mel = torch.log(mel_spec + self.eps)

        # Pad / trim to exactly n_frames
        T_cur = log_mel.size(-1)
        if T_cur < self.n_frames:
            log_mel = nn.functional.pad(log_mel, (0, self.n_frames - T_cur))
        elif T_cur > self.n_frames:
            log_mel = log_mel[..., :self.n_frames]

        # Per-utterance mean/var normalization (stabilizes training)
        if self.normalize:
            mean = log_mel.mean(dim=(-1, -2), keepdim=True)
            std = log_mel.std(dim=(-1, -2), keepdim=True) + 1e-5
            log_mel = (log_mel - mean) / std

        # Reshape to (B, 1, n_frames, n_mels) — channels-first for Conv2D
        log_mel = log_mel.transpose(-1, -2).unsqueeze(1)
        return log_mel
