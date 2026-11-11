import os
import random
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchaudio
from torch.utils.data import Dataset


class UrbanSoundDataset(Dataset):
    """
    Sound event classification dataset (UrbanSound8K-style format).

    Expects:
      root/
        metadata.csv          (slice_file_name, fold, classID, class, ...)
          fold1/  *.wav
          fold2/  *.wav
          ...
          fold10/ *.wav

    Returns: (waveform: Tensor[clip_len], label: int)
    """

    def __init__(self,
                 root,
                 metadata_csv,
                 folds,                       # list[int], e.g. [1,2,...,8] for train
                 sample_rate=22050,
                 clip_seconds=4.0,
                 augment=True,
                 noise_dir=None,
                 audio_subdir=""):
        self.root = root
        self.audio_dir = os.path.join(root, audio_subdir)
        self.sample_rate = sample_rate
        self.clip_len = int(sample_rate * clip_seconds)
        self.augment = augment

        # Load and filter metadata by fold
        df = pd.read_csv(metadata_csv)
        df = df[df["fold"].isin(folds)].reset_index(drop=True)
        self.df = df

        # Build (path, label) list
        self.samples = [
            (
                os.path.join(self.audio_dir, f"fold{row.fold}", row.slice_file_name),
                int(row.classID),
            )
            for row in df.itertuples()
        ]

        # Class info
        self.num_classes = int(df["classID"].max()) + 1
        self.class_names = (
            df.drop_duplicates("classID")
              .sort_values("classID")["class"].tolist()
        )

        # Optional noise files for augmentation
        self.noise_files = []
        if noise_dir and os.path.isdir(noise_dir):
            import glob
            self.noise_files = glob.glob(os.path.join(noise_dir, "*.wav"))

    # ---------------------------------------------------------------- #
    def __len__(self):
        return len(self.samples)

    # ---------------------------------------------------------------- #
    def _load_wav(self, path):
        wav, sr = torchaudio.load(path)
        if sr != self.sample_rate:
            wav = torchaudio.functional.resample(wav, sr, self.sample_rate)
        if wav.size(0) > 1:
            wav = wav.mean(dim=0, keepdim=True)        # mix down to mono
        return wav.squeeze(0)                          # (num_samples,)

    def _fix_length(self, wav):
        if wav.size(0) >= self.clip_len:
            start = random.randint(0, wav.size(0) - self.clip_len)
            return wav[start:start + self.clip_len]
        pad = self.clip_len - wav.size(0)
        left = random.randint(0, pad) if self.augment else 0
        return F.pad(wav, (left, pad - left))

    def _augment(self, wav):
        # Random gain ±6 dB
        gain_db = random.uniform(-6, 6)
        wav = wav * (10 ** (gain_db / 20))

        # Background noise mix
        if self.noise_files and random.random() < 0.5:
            noise = self._fix_length(self._load_wav(random.choice(self.noise_files)))
            snr_db = random.uniform(5, 25)
            sig_p = wav.pow(2).mean()
            noise_p = noise.pow(2).mean() + 1e-9
            scale = torch.sqrt(sig_p / (noise_p * 10 ** (snr_db / 10)))
            wav = wav + scale * noise

        # Time shift up to ±200 ms
        max_shift = int(self.sample_rate * 0.2)
        wav = torch.roll(wav, shifts=random.randint(-max_shift, max_shift))
        return wav

    # ---------------------------------------------------------------- #
    def __getitem__(self, idx):
        path, label = self.samples[idx]
        wav = self._load_wav(path)
        wav = self._fix_length(wav)
        if self.augment:
            wav = self._augment(wav)
        wav = torch.clamp(wav, -1.0, 1.0)
        return wav, label
