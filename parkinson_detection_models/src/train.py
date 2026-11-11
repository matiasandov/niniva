import torch
from torch import nn
from torch.utils.data import DataLoader
from collections import defaultdict   # 👈 NEW
import copy


def train_tinycrnn(model,
                   feature_extractor,
                   spec_augment,
                   train_dataset,
                   val_dataset=None,
                   epochs=20,
                   batch_size=256,
                   lr=1e-3,
                   device="cuda",
                   class_weights=None,
                   patience=5,
                   class_names=None,            # 👈 NEW (optional, for nicer logs)
                   log_per_class=False):        # 👈 NEW (toggle on for multi-class)
    """
    End-to-end Tiny-CRNN trainer with on-GPU feature extraction and early stopping.

    Args:
        ...
        class_names    : Optional list[str] — used to label per-class accuracy logs.
        log_per_class  : If True, prints per-class validation accuracy each epoch.
                         Recommended for multi-class tasks (e.g. UrbanSound8K).
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

    best_val_loss = float('inf')
    epochs_no_improve = 0
    best_model_weights = copy.deepcopy(model.state_dict())

    print("🎯 Starting training loop...")
    for epoch in range(epochs):
        print(f"\n🔄 Epoch {epoch+1}/{epochs}")

        # ---- TRAIN ----
        print("📈 TRAIN phase...")
        model.train()
        spec_augment.train()

        running_loss, correct, total = 0.0, 0, 0
        for batch_idx, (wav, label) in enumerate(train_loader):
            wav, label = wav.to(device), label.to(device)

            feats = feature_extractor(wav)
            feats = spec_augment(feats)

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

        # ---- VAL & EARLY STOPPING ----
        if val_loader:
            print("🎯 VAL phase...")
            model.eval()
            v_running_loss, v_correct, v_total = 0.0, 0, 0

            # 👇 NEW: per-class trackers
            class_correct = defaultdict(int)
            class_total = defaultdict(int)

            with torch.no_grad():
                for wav, label in val_loader:
                    wav, label = wav.to(device), label.to(device)
                    feats = feature_extractor(wav)
                    logits = model(feats)

                    v_loss = criterion(logits, label)
                    v_running_loss += v_loss.item() * wav.size(0)

                    preds = logits.argmax(-1)
                    v_correct += (preds == label).sum().item()
                    v_total += wav.size(0)

                    # 👇 NEW: accumulate per-class correct/total
                    if log_per_class:
                        for p, t in zip(preds.cpu(), label.cpu()):
                            t_int = t.item()
                            class_total[t_int] += 1
                            if p.item() == t_int:
                                class_correct[t_int] += 1

            val_loss = v_running_loss / v_total
            val_acc = v_correct / v_total
            print(f"✅            val loss={val_loss:.4f}  val acc={val_acc:.3f}")

            # 👇 NEW: print per-class accuracy
            if log_per_class and class_total:
                print("   📊 Per-class validation accuracy:")
                for cls in sorted(class_total.keys()):
                    name = class_names[cls] if class_names else f"class {cls}"
                    acc = class_correct[cls] / class_total[cls]
                    print(f"      {name:<20s} {acc:.3f}  "
                          f"({class_correct[cls]}/{class_total[cls]})")

            # ---- Early Stopping ----
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                epochs_no_improve = 0
                best_model_weights = copy.deepcopy(model.state_dict())
                print(f"🌟 New best validation loss: {best_val_loss:.4f}! Saving weights.")
            else:
                epochs_no_improve += 1
                print(f"⚠️ No improvement in validation loss for {epochs_no_improve} epoch(s).")

                if epochs_no_improve >= patience:
                    print(f"🛑 Early stopping triggered! Restoring best model weights "
                          f"from epoch {epoch + 1 - patience}.")
                    model.load_state_dict(best_model_weights)
                    break

    print("\n🎉 Training complete!")
    return model
