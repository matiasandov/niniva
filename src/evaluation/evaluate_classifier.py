import os
import json
import torch
import numpy as np
import matplotlib.pyplot as plt
from torch.utils.data import DataLoader
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    classification_report,
    f1_score,
    top_k_accuracy_score,
)

from src.dataset_urban_sound import UrbanSoundDataset
from src.features import LFBEFeatureExtractor
from src.models.tiny_crnn import TinyCRNN


class EndToEndModel(torch.nn.Module):
    def __init__(self, feature_extractor, crnn_model):
        super().__init__()
        self.fe = feature_extractor
        self.model = crnn_model

    def forward(self, x):
        feats = self.fe(x)
        return self.model(feats)


@torch.no_grad()
def collect_predictions(model, loader, device):
    """Returns (logits[N, C], labels[N]) as numpy arrays."""
    model.eval()
    all_logits, all_labels = [], []
    for wav, label in loader:
        wav = wav.to(device)
        logits = model(wav)
        all_logits.append(logits.cpu().numpy())
        all_labels.append(label.numpy())
    return np.concatenate(all_logits), np.concatenate(all_labels)


def plot_confusion_matrix(cm, class_names, save_path, normalize=True):
    if normalize:
        cm = cm.astype(float) / cm.sum(axis=1, keepdims=True).clip(min=1e-9)

    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(cm, cmap="Blues", vmin=0, vmax=1 if normalize else None)
    ax.figure.colorbar(im, ax=ax)
    ax.set(
        xticks=np.arange(len(class_names)),
        yticks=np.arange(len(class_names)),
        xticklabels=class_names,
        yticklabels=class_names,
        ylabel="True label",
        xlabel="Predicted label",
        title="Confusion Matrix" + (" (normalized)" if normalize else ""),
    )
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    fmt = ".2f" if normalize else "d"
    thresh = cm.max() / 2.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, format(cm[i, j], fmt),
                    ha="center", va="center",
                    color="white" if cm[i, j] > thresh else "black",
                    fontsize=8)

    fig.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close(fig)


def evaluate_model(run_dir, data_root, metadata_csv):
    print(f"🔍 Evaluating model from: {run_dir}")
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # 1. Load config
    with open(os.path.join(run_dir, "config.json"), "r") as f:
        config = json.load(f)
    print("✅ Configuration loaded.")

    # 2. Rebuild feature extractor + model
    feature_extractor = LFBEFeatureExtractor(
        sample_rate=config["sample_rate"],
        n_mels=config["n_mels"],
        n_frames=config["n_frames"],
    )
    model = TinyCRNN(
        n_mels=config["n_mels"],
        n_frames=config["n_frames"],
        conv_channels=config["conv_channels"],
        gru_hidden=config["gru_hidden"],
        fc_hidden=config["fc_hidden"],
        use_attention=config["use_attention"],
        num_classes=config["num_classes"],
    )

    # 3. Load weights
    model.load_state_dict(torch.load(os.path.join(run_dir, "model.pth"),
                                     map_location=device))
    print("✅ Model weights loaded.")

    e2e_model = EndToEndModel(feature_extractor, model).to(device).eval()

    # 4. Test dataset (held-out fold)
    test_ds = UrbanSoundDataset(
        root=data_root,
        metadata_csv=metadata_csv,
        folds=config["test_folds"],         # 👈 fold 10 from training config
        sample_rate=config["sample_rate"],
        clip_seconds=config["clip_seconds"],
        augment=False,
    )
    test_loader = DataLoader(test_ds, batch_size=config["batch_size"],
                             shuffle=False, num_workers=2)
    print(f"📂 Test dataset loaded: {len(test_ds)} samples "
          f"(folds {config['test_folds']})")

    class_names = config.get("class_names") or test_ds.class_names

    # 5. Predict
    print("\n🏃 Running predictions on test set...")
    logits, labels = collect_predictions(e2e_model, test_loader, device)
    preds = logits.argmax(axis=1)
    probs = torch.softmax(torch.from_numpy(logits), dim=1).numpy()

    # 6. Metrics
    acc = accuracy_score(labels, preds)
    macro_f1 = f1_score(labels, preds, average="macro")
    weighted_f1 = f1_score(labels, preds, average="weighted")
    top3 = top_k_accuracy_score(labels, probs, k=3,
                                labels=np.arange(config["num_classes"]))

    cm = confusion_matrix(labels, preds, labels=np.arange(config["num_classes"]))
    report_dict = classification_report(
        labels, preds,
        labels=np.arange(config["num_classes"]),
        target_names=class_names,
        output_dict=True,
        zero_division=0,
    )

    # 7. Print
    print("\n" + "=" * 50)
    print("📊 EVALUATION RESULTS")
    print("=" * 50)
    print(f"Accuracy        : {acc:.4f}")
    print(f"Top-3 Accuracy  : {top3:.4f}")
    print(f"Macro F1        : {macro_f1:.4f}")
    print(f"Weighted F1     : {weighted_f1:.4f}")
    print("\nPer-class report:")
    print(classification_report(
        labels, preds,
        labels=np.arange(config["num_classes"]),
        target_names=class_names,
        zero_division=0,
    ))

    # 8. Save results
    results = {
        "test_samples": len(test_ds),
        "accuracy": float(acc),
        "top3_accuracy": float(top3),
        "macro_f1": float(macro_f1),
        "weighted_f1": float(weighted_f1),
        "per_class": report_dict,
        "confusion_matrix": cm.tolist(),
        "class_names": class_names,
    }
    with open(os.path.join(run_dir, "eval_results.json"), "w") as f:
        json.dump(results, f, indent=4)

    # 9. Confusion matrix plots (raw + normalized)
    plot_confusion_matrix(cm, class_names,
                          os.path.join(run_dir, "confusion_matrix.png"),
                          normalize=True)
    plot_confusion_matrix(cm, class_names,
                          os.path.join(run_dir, "confusion_matrix_counts.png"),
                          normalize=False)
    print(f"\n📈 Saved results and confusion matrices to: {run_dir}")


if __name__ == "__main__":
    RUN_TO_EVALUATE = r"saved_models\sound_events\tiny_crnn_urbansound_v20260510_222414"
    DATA_ROOT = r"data\audio_data\sounds"
    METADATA_CSV = os.path.join(DATA_ROOT, "UrbanSound8K.csv")

    evaluate_model(RUN_TO_EVALUATE, DATA_ROOT, METADATA_CSV)
