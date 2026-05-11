import os
import json
from datetime import datetime
import torch

from src.augment import SpecAugment
from src.dataset import WakewordAudioDataset
from src.features import LFBEFeatureExtractor
from src.models.tiny_crnn import TinyCRNN
from src.train import train_tinycrnn

# Be sure to have prepared the data in train and val before
# script to do it is in scripts/data/pipelines/wakeword_train_val_split.py

if __name__ == "__main__":
    print("🚀 Starting training script...\n")
    device = "cuda" if torch.cuda.is_available() else "cpu"

    print(f"⚡ Device: {device}")
    if device == "cuda":
        print(f"   GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")

    # 👇 1. Define all your parameters in one central config dictionary 👇
    config = {
        "sample_rate": 16000,
        "clip_seconds": 1.5,
        "n_mels": 64,
        "n_frames": 100,
        "conv_channels": (64, 64, 64),
        "gru_hidden": 128,          # Assuming default from your model
        "use_attention": True,      # Assuming default from your model
        "batch_size": 256,
        "learning_rate": 1e-3,
        "epochs": 50,
        "patience": 5,
        "class_weights": [1.0, 3.0]
    }

    # 👇 2. Create a dynamic version name based on the current timestamp 👇
    version = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_name = f"tiny_crnn_v{version}"
    save_dir = os.path.join("saved_models/wakeword_stop", run_name)
    os.makedirs(save_dir, exist_ok=True)
    print(f"\n📁 Created run directory: {save_dir}")

    print("\n📦 Preparing datasets and model...")
    feature_extractor = LFBEFeatureExtractor(
        sample_rate=config["sample_rate"], 
        n_mels=config["n_mels"], 
        n_frames=config["n_frames"]
    )
    spec_augment = SpecAugment()
    
    print("✅ Feature extractor created")
    print(f"   Output shape: (B, 1, {config['n_frames']}, {config['n_mels']})")    

    print("\n🧠 Building Tiny CRNN model...")
    model = TinyCRNN(
        n_mels=config["n_mels"], 
        n_frames=config["n_frames"],
        conv_channels=config["conv_channels"],
        # Add your gru_hidden/use_attention here if your TinyCRNN init takes them
    )

    print("📂 Loading datasets...")
    train_ds = WakewordAudioDataset(
        root=r"data\wakewords\stop\dataset_split\train",
        sample_rate=config["sample_rate"],
        clip_seconds=config["clip_seconds"],
        augment=True,
    )
    val_ds = WakewordAudioDataset(
        root=r"data\wakewords\stop\dataset_split\val",
        sample_rate=config["sample_rate"],
        clip_seconds=config["clip_seconds"],
        augment=False,
    )
    print(f"✅ Train dataset loaded: {len(train_ds)} samples")
    print(f"✅ Val dataset loaded: {len(val_ds)} samples")

    class_weights = torch.tensor(config["class_weights"])
    print(f"⚖️  Class weights: negative={class_weights[0]}, positive={class_weights[1]}")

    print("\n" + "="*60)
    print(f"🎬 Starting training for {run_name}...")
    print("="*60 + "\n")

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
        patience=config["patience"]
    )

    # 👇 3. Save the best model weights 👇
    model_save_path = os.path.join(save_dir, f"model.pth")
    torch.save(trained_model.state_dict(), model_save_path)
    print(f"\n💾 Model weights saved to: {model_save_path}")

    # 👇 4. Save the hyperparameter configuration 👇
    config_save_path = os.path.join(save_dir, "config.json")
    with open(config_save_path, "w") as f:
        json.dump(config, f, indent=4)
    print(f"📝 Run configuration saved to: {config_save_path}")
    print("🎉 Run completely saved and finished!")