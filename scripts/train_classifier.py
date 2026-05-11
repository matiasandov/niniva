import os
import json
from datetime import datetime
import torch

from src.augment import SpecAugment
from src.dataset import UrbanSoundDataset
from src.features import LFBEFeatureExtractor
from src.models.tiny_crnn import TinyCRNN
from src.train import train_tinycrnn


if __name__ == "__main__":
    print("🚀 Starting UrbanSound classification training script...\n")
    device = "cuda" if torch.cuda.is_available() else "cpu"

    print(f"⚡ Device: {device}")
    if device == "cuda":
        print(f"   GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")

    # ----------------------------------------------------------------------
    # 1. Central configuration
    # ----------------------------------------------------------------------
    config = {
        # Audio
        "sample_rate": 22050,
        "clip_seconds": 4.0,        # UrbanSound8K clips are up to 4 sec

        # Features
        "n_mels": 64,
        "n_frames": 200,            # 4 sec @ 10ms hop ≈ 400 frames; 200 with 20ms hop or trimmed

        # Model
        "conv_channels": (64, 64, 128),
        "gru_hidden": 128,
        "fc_hidden": 128,
        "use_attention": True,
        "num_classes": 10,          # UrbanSound8K has 10 classes

        # Training
        "batch_size": 128,
        "learning_rate": 1e-3,
        "epochs": 60,
        "patience": 8,

        # Folds (UrbanSound8K has folds 1..10)
        "train_folds": [1, 2, 3, 4, 5, 6, 7, 8],
        "val_folds":   [9],
        "test_folds":  [10],

        # Class weights — set to None to use uniform weighting,
        # or compute from class frequencies (see below)
        "use_class_weights": True,
    }

    # ----------------------------------------------------------------------
    # 2. Run directory
    # ----------------------------------------------------------------------
    version = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_name = f"tiny_crnn_urbansound_v{version}"
    save_dir = os.path.join("saved_models/sound_events", run_name)
    os.makedirs(save_dir, exist_ok=True)
    print(f"\n📁 Created run directory: {save_dir}")

    # ----------------------------------------------------------------------
    # 3. Feature extractor + SpecAugment
    # ----------------------------------------------------------------------
    print("\n📦 Preparing feature extractor and augmentation...")
    feature_extractor = LFBEFeatureExtractor(
        sample_rate=config["sample_rate"],
        n_mels=config["n_mels"],
        n_frames=config["n_frames"],
    )
    spec_augment = SpecAugment(
        freq_mask_param=12,
        n_freq_masks=2,
        time_mask_param=30,
        n_time_masks=2,
        time_mask_ratio=0.2,
        prob=0.8,
    )
    print("✅ Feature extractor created")
    print(f"   Output shape: (B, 1, {config['n_frames']}, {config['n_mels']})")

    # ----------------------------------------------------------------------
    # 4. Datasets
    # ----------------------------------------------------------------------
    DATA_ROOT = r"data\urbansound8k"               # adjust to your path
    METADATA_CSV = os.path.join(DATA_ROOT, "metadata", "UrbanSound8K.csv")

    print("\n📂 Loading datasets...")
    train_ds = UrbanSoundDataset(
        root=DATA_ROOT,
        metadata_csv=METADATA_CSV,
        folds=config["train_folds"],
        sample_rate=config["sample_rate"],
        clip_seconds=config["clip_seconds"],
        augment=True,
    )
    val_ds = UrbanSoundDataset(
        root=DATA_ROOT,
        metadata_csv=METADATA_CSV,
        folds=config["val_folds"],
        sample_rate=config["sample_rate"],
        clip_seconds=config["clip_seconds"],
        augment=False,
    )
    print(f"✅ Train dataset: {len(train_ds)} samples (folds {config['train_folds']})")
    print(f"✅ Val   dataset: {len(val_ds)} samples (folds {config['val_folds']})")
    print(f"✅ Classes ({train_ds.num_classes}): {train_ds.class_names}")

    config["class_names"] = train_ds.class_names    # save for later

    # ----------------------------------------------------------------------
    # 5. Class weights (inverse frequency)
    # ----------------------------------------------------------------------
    class_weights = None
    if config["use_class_weights"]:
        counts = torch.zeros(config["num_classes"])
        for _, lbl in train_ds.samples:
            counts[lbl] += 1
        class_weights = counts.sum() / (config["num_classes"] * counts.clamp(min=1))
        print(f"⚖️  Class weights (inverse-freq): {class_weights.tolist()}")
        config["class_weights"] = class_weights.tolist()

    # ----------------------------------------------------------------------
    # 6. Model
    # ----------------------------------------------------------------------
    print("\n🧠 Building Tiny-CRNN model...")
    model = TinyCRNN(
        n_mels=config["n_mels"],
        n_frames=config["n_frames"],
        conv_channels=config["conv_channels"],
        gru_hidden=config["gru_hidden"],
        fc_hidden=config["fc_hidden"],
        use_attention=config["use_attention"],
        num_classes=config["num_classes"],
    )
    n_params = sum(p.numel() for p in model.parameters())
    print(f"✅ Model built: {n_params:,} parameters")
    config["num_parameters"] = n_params

    # ----------------------------------------------------------------------
    # 7. Train
    # ----------------------------------------------------------------------
    print("\n" + "=" * 60)
    print(f"🎬 Starting training for {run_name}...")
    print("=" * 60 + "\n")

    trained_model = train_tinycrnn(
        model,
        feature_extractor,
        spec_augment,
        train_ds,
        val_ds,
        epochs=config["epochs"],
        batch_size=config["batch_size"],
        lr=config["learning_rate"],
        device=device,
        class_weights=class_weights,
        patience=config["patience"],
    )

    # ----------------------------------------------------------------------
    # 8. Save model + config
    # ----------------------------------------------------------------------
    model_save_path = os.path.join(save_dir, "model.pth")
    torch.save(trained_model.state_dict(), model_save_path)
    print(f"\n💾 Model weights saved to: {model_save_path}")

    config_save_path = os.path.join(save_dir, "config.json")
    with open(config_save_path, "w") as f:
        json.dump(config, f, indent=4)
    print(f"📝 Run configuration saved to: {config_save_path}")
    print("🎉 Run completely saved and finished!")
