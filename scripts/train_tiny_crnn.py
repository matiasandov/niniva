from src.augment import SpecAugment
from src.dataset import WakewordAudioDataset
from src.features import LFBEFeatureExtractor
from src.models.tiny_crnn import TinyCRNN
from src.train import train_tinycrnn
import torch

# Be sure to have prepared the data in train and val before
# script to do it is in scripts/data/pipelines/wakeword_train_val_split.py

if __name__ == "__main__":
    print("🚀 Starting training script...\n")
    device = "cuda" if torch.cuda.is_available() else "cpu"

    print(f"⚡ Device: {device}")
    if device == "cuda":
        print(f"   GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    print("\n📦 Preparing datasets and model...")
    feature_extractor = LFBEFeatureExtractor(
        sample_rate=16000, n_mels=64, n_frames=100,
    )
    
    print("✅ Feature extractor created")
    print("   Output shape: (B, 1, n_frames, n_mels) = (B, 1, 100, 64)")    

    print("\n🧠 Building Tiny CRNN model...")
    model = TinyCRNN(
        n_mels=64, n_frames=100,
        conv_channels=(64, 64, 64),
        conv_kernels=((5, 5), (5, 5), (10, 4)),
        conv_strides=((1, 2), (2, 2), (1, 1)),
        gru_hidden=64, fc_hidden=64,
        use_attention=True,
    )
    print("✅ Model created")
    total_params = sum(p.numel() for p in model.parameters())
    print(f"   Total parameters: {total_params:,}")
    
    print("\n🎨 Creating SpecAugment...")
    spec_augment = SpecAugment(
        freq_mask_param=8,      # mask up to 8 of 64 mel bins
        n_freq_masks=2,
        time_mask_param=25,     # mask up to 25 of 100 frames
        n_time_masks=2,
        time_mask_ratio=0.2,    # but never more than 20% of frames total
        mask_value=0.0,         # safe because features are normalized
        prob=0.8,               # augment 80% of training samples
    )
    print("✅ SpecAugment configured\n")

    """
    ########  Note on datasets ########
    The WakewordAudioDataset class in src/dataset.py is designed to load your audio data
        Loads (audio, label) pairs from disk.
            Labels: 0 = negative (non-wakeword), 1 = positive (wakeword)
        Expected directory layout:
            root/
            positive/  *.wav    # contains the wakeword
            negative/  *.wav    # any other speech / background

        Audio is returned as a fixed-length waveform (clip_seconds).
    """
    print("📂 Loading datasets...")
    train_ds = WakewordAudioDataset(
        root="data/train",
        sample_rate=16000,
        clip_seconds=1.5,            # ⚠️ longer for "Call 911" — see Part 4
        augment=True,
    )
    val_ds = WakewordAudioDataset(
        root="data/val", augment=False,
    )
    print(f"✅ Train dataset loaded: {len(train_ds)} samples")
    print(f"✅ Val dataset loaded: {len(val_ds)} samples")

    # If your dataset is unbalanced, weight the loss
    class_weights = torch.tensor([1.0, 3.0])     # negatives : positives
    print(f"⚖️  Class weights: negative={class_weights[0]}, positive={class_weights[1]}")

    print("\n" + "="*60)
    print("🎬 Starting training...")
    print("="*60 + "\n")

    train_tinycrnn(
        model, 
        feature_extractor, 
        spec_augment,
        train_ds, val_ds,
        epochs=20, batch_size=256, lr=1e-3, device=device,
    )
