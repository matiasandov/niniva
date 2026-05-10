import os
import random
import glob
import torch
from torch import nn
from torch.utils.data import Dataset
import torchaudio


class WakewordAudioDataset(Dataset):
    """
    Loads (audio, label) pairs from disk.
    Expected directory layout:
        root/
          positive/  *.wav    # contains the wakeword
          negative/  *.wav    # any other speech / background

    Audio is returned as a fixed-length waveform (clip_seconds).
    """
    def __init__(self,
                 root,
                 sample_rate=16000,
                 clip_seconds=1.0, #can change depending on wake word
                 augment=True,
                 noise_dir=None):
        self.sample_rate = sample_rate
        self.clip_len = int(sample_rate * clip_seconds)
        self.augment = augment

        self.samples = []
        for label, sub in [(1, "positive"), (0, "negative")]:
            for f in glob.glob(os.path.join(root, sub, "*.wav")):
                self.samples.append((f, label))
        random.shuffle(self.samples)

        self.noise_files = (
            glob.glob(os.path.join(noise_dir, "*.wav")) if noise_dir else []
        )

    def __len__(self):
        return len(self.samples)

    def _load_wav(self, path):
        wav, sr = torchaudio.load(path)
        if sr != self.sample_rate:
            wav = torchaudio.functional.resample(wav, sr, self.sample_rate)
        if wav.size(0) > 1:                         # mix down to mono
            wav = wav.mean(dim=0, keepdim=True)
        return wav.squeeze(0)                        # (num_samples,)

    def _fix_length(self, wav):
        if wav.size(0) >= self.clip_len:
            start = random.randint(0, wav.size(0) - self.clip_len)
            return wav[start:start + self.clip_len]
        pad = self.clip_len - wav.size(0)
        # Random pad on left/right so the wakeword position varies in the clip
        left = random.randint(0, pad)
        return nn.functional.pad(wav, (left, pad - left))

    def _augment(self, wav):
        # 1. Random gain (±6 dB) — mimics AFE gain variations
        gain_db = random.uniform(-6, 6)
        wav = wav * (10 ** (gain_db / 20))

        # 2. Add background noise at random SNR
        if self.noise_files and random.random() < 0.5:
            noise_path = random.choice(self.noise_files)
            noise = self._fix_length(self._load_wav(noise_path))
            snr_db = random.uniform(5, 25)
            sig_p = wav.pow(2).mean()
            noise_p = noise.pow(2).mean() + 1e-9
            scale = torch.sqrt(sig_p / (noise_p * 10 ** (snr_db / 10)))
            wav = wav + scale * noise

        # 3. Light time shift (±100 ms)
        shift = random.randint(-1600, 1600)
        wav = torch.roll(wav, shifts=shift)
        return wav

    def __getitem__(self, idx):
        path, label = self.samples[idx]
        wav = self._load_wav(path)
        wav = self._fix_length(wav)
        if self.augment:
            wav = self._augment(wav)
        wav = torch.clamp(wav, -1.0, 1.0)
        return wav, label

