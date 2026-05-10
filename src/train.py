import torch
from torch import nn

from src.dataset import WakewordAudioDataset
import torch.nn.functional as F
from torch.utils.data import DataLoader


def train_tinycrnn(model,
                   feature_extractor,
                   spec_augment,
                   train_dataset,
                   val_dataset=None,
                   epochs=20,
                   batch_size=256,
                   lr=1e-3,
                   device="cuda",
                   class_weights=None):
    """
    End-to-end Tiny-CRNN trainer with on-GPU feature extraction.
    """
    print("🚀 Starting train_tinycrnn...")
    print(f"⚡ Device: {device}, Epochs: {epochs}, Batch size: {batch_size}, LR: {lr}")
    
    model.to(device)
    feature_extractor.to(device)
    spec_augment.to(device)
    print("✅ Models moved to device") 

    print("📊 Creating data loaders...")
    train_loader = DataLoader(train_dataset, batch_size=batch_size,
                              shuffle=True, num_workers=4, pin_memory=True)
    val_loader = (DataLoader(val_dataset, batch_size=batch_size,
                             shuffle=False, num_workers=2, pin_memory=True)
                  if val_dataset else None)
    print(f"📊 Train batches: {len(train_loader)}, Val batches: {len(val_loader) if val_loader else 0}")

    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    if class_weights is not None:
        class_weights = class_weights.to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    print("✅ Optimizer and loss criterion initialized")

    print("🎯 Starting training loop...")
    for epoch in range(epochs):
        print(f"\n🔄 Epoch {epoch+1}/{epochs}")
        
        # ---- TRAIN ----
        print("📈 TRAIN phase...")
        model.train()
        spec_augment.train()                      # ← enables masking

        running_loss, correct, total = 0.0, 0, 0
        for wav, label in train_loader:
            wav, label = wav.to(device), label.to(device)

            feats = feature_extractor(wav)              # (B, 1, 100, n_mels)
            feats = spec_augment(feats)           # ← apply SpecAugment

            logits = model(feats)
            loss = criterion(logits, label)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * wav.size(0)
            correct += (logits.argmax(-1) == label).sum().item()
            total += wav.size(0)
            
            if batch_idx % 10 == 0:
                print(f"  📉 Batch {batch_idx}/{len(train_loader)} - Loss: {loss.item():.4f}")

        print(f"✅ [epoch {epoch+1:02d}] train loss={running_loss/total:.4f}  "
              f"acc={correct/total:.3f}")

        # ---- VAL ----
        if val_loader:
            print("🎯 VAL phase...")
            model.eval()
            v_correct, v_total = 0, 0
            with torch.no_grad():
                for wav, label in val_loader:
                    wav, label = wav.to(device), label.to(device)
                    feats = feature_extractor(wav)
                    logits = model(feats)
                    v_correct += (logits.argmax(-1) == label).sum().item()
                    v_total += wav.size(0)
            print(f"✅            val acc={v_correct/v_total:.3f}")

    print("\n🎉 Training complete!")
    return model

