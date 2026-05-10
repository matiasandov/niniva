from src.augment import SpecAugment
from src.dataset import WakewordAudioDataset
from src.features import LFBEFeatureExtractor
from src.models.tiny_crnn import TinyCRNN
from src.train import train_tinycrnn
import torch
if __name__ == "__main__":
    device = "cuda" if torch.cuda.is_available() else "cpu"

    feature_extractor = LFBEFeatureExtractor(
        sample_rate=16000, n_mels=64, n_frames=100,
    )
    

    model = TinyCRNN(
        n_mels=64, n_frames=100,
        conv_channels=(64, 64, 64),
        conv_kernels=((5, 5), (5, 5), (10, 4)),
        conv_strides=((1, 2), (2, 2), (1, 1)),
        gru_hidden=64, fc_hidden=64,
        use_attention=True,
    )
    
    spec_augment = SpecAugment(
        freq_mask_param=8,      # mask up to 8 of 64 mel bins
        n_freq_masks=2,
        time_mask_param=25,     # mask up to 25 of 100 frames
        n_time_masks=2,
        time_mask_ratio=0.2,    # but never more than 20% of frames total
        mask_value=0.0,         # safe because features are normalized
        prob=0.8,               # augment 80% of training samples
    )

    train_ds = WakewordAudioDataset(
        root="data/train",
        sample_rate=16000,
        clip_seconds=1.5,            # ⚠️ longer for "Call 911" — see Part 4
        augment=True,
        noise_dir="data/noise",
    )
    val_ds = WakewordAudioDataset(
        root="data/val", augment=False,
    )

    # If your dataset is unbalanced, weight the loss
    class_weights = torch.tensor([1.0, 3.0])     # negatives : positives

    train_tinycrnn(
        model, 
        feature_extractor, 
        spec_augment,
        train_ds, val_ds,
        epochs=20, batch_size=256, lr=1e-3, device=device,
    )
