## 📁 Recommended Project Layout

```
tiny-crnn-wakeword/
├── pyproject.toml
├── README.md
├── LICENSE
├── src/
│   └── tiny_crnn_wakeword/
│       ├── __init__.py
│       ├── py.typed
│       ├── model.py              # TinyCRNN, attention, conv block
│       ├── features.py           # LFBEFeatureExtractor
│       ├── augment.py            # SpecAugment, waveform augmentations
│       ├── dataset.py            # WakewordAudioDataset
│       ├── train.py              # training loop
│       ├── eval.py               # FA / DET metrics
│       └── streaming.py          # parallel & high-dim GRU streaming
├── tests/
│   ├── test_model.py
│   ├── test_features.py
│   └── test_augment.py
├── configs/
│   └── crnn_239k.yaml
└── scripts/
    ├── train_alexa.py
    └── train_call_911.py
```

---

## 🚀 Setup Instructions

### Option 1: Standard `pip` + venv (simplest)
![image.png](attachment:74f25b2d-5cd7-460d-a10c-6a2bd0df49d7:image.png)

Runnning scripts as modules

python -m scripts.data.pipelineswakeword_train_val_split

# Poetry
poetry env activate
poetry add -

## running a file
python -m scripts.train_tiny_crnn